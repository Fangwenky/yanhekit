# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "requests>=2.31",
# ]
# ///
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


API = "https://member.bilibili.com/x/bcut/rubick-interface"
CREATE_RESOURCE = f"{API}/resource/create"
COMPLETE_RESOURCE = f"{API}/resource/create/complete"
CREATE_TASK = f"{API}/task"
TASK_RESULT = f"{API}/task/result"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    ),
}

VIDEO_EXTS = {".mp4"}
RECORDING_PREFIXES = ("camera", "screen")


@dataclass
class Segment:
    start_ms: int
    end_ms: int
    text: str


def _print(msg: str, end: str = "") -> None:
    sys.stdout.write(f"\r\033[2K{msg}{end}")
    sys.stdout.flush()


def _begin(label: str) -> None:
    """Clear current line, write label, save cursor for _tick() calls."""
    sys.stdout.write(f"\r\033[2K{label}\033[s")
    sys.stdout.flush()


def _tick(suffix: str) -> None:
    """Restore cursor to last _begin() position and overwrite suffix."""
    sys.stdout.write(f"\033[u\033[K{suffix}")
    sys.stdout.flush()


def _with_elapsed(label: str, fn: Callable[[], Any]) -> Any:
    """Run fn() while ticking elapsed seconds on the current line every second."""
    done = threading.Event()
    start = time.monotonic()
    _begin(f"{label} ")

    def tick() -> None:
        while not done.wait(1.0):
            _tick(f"{int(time.monotonic() - start)}s")

    t = threading.Thread(target=tick, daemon=True)
    t.start()
    try:
        return fn()
    finally:
        done.set()
        t.join()


def _retry(
    fn: Callable[..., Any],
    *args: Any,
    retries: int,
    on_retry: Callable[[int, float], None] | None = None,
    **kwargs: Any,
) -> Any:
    for attempt in range(1, retries + 1):
        try:
            return fn(*args, **kwargs)
        except Exception:
            if attempt == retries:
                raise
            delay = 2.0 ** (attempt - 1)
            if on_retry:
                on_retry(attempt, delay)
            time.sleep(delay)


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def request_data(response: Any) -> dict[str, Any]:
    try:
        response.raise_for_status()
    except Exception as exc:
        body = response.text.strip()
        if len(body) > 500:
            body = body[:500] + "..."
        raise RuntimeError(
            f"bijian http error {response.status_code} {response.reason}: {body}"
        ) from exc
    payload = response.json()
    if payload.get("code", 0):
        message = payload.get("message") or payload.get("msg") or payload
        raise RuntimeError(f"bijian api error: {message}")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise RuntimeError(f"unexpected bijian response: {payload}")
    return data


def run_ffmpeg(video: Path, audio: Path, overwrite: bool) -> None:
    if audio.exists() and not overwrite:
        return
    audio.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(video),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "libmp3lame",
            "-b:a",
            "48k",
            str(audio),
        ],
        check=True,
    )


def upload_audio(
    session: Any,
    audio: Path,
    on_progress: Callable[[int, int], None] | None = None,
) -> str:
    audio_size = audio.stat().st_size
    audio_type = audio.suffix.lower().lstrip(".")

    meta = request_data(
        session.post(
            CREATE_RESOURCE,
            data={
                "type": 2,
                "name": audio.name,
                "size": audio_size,
                "resource_file_type": audio_type,
                "model_id": 7,
            },
            headers=HEADERS,
            timeout=60,
        )
    )

    per_size = int(meta["per_size"])
    upload_urls = meta["upload_urls"]
    etags = []
    with audio.open("rb") as f:
        for index, url in enumerate(upload_urls):
            if on_progress:
                on_progress(index + 1, len(upload_urls))
            f.seek(index * per_size)
            response = session.put(
                url,
                data=f.read(per_size),
                headers=HEADERS,
                timeout=120,
            )
            response.raise_for_status()
            etag = response.headers.get("Etag") or response.headers.get("ETag")
            if not etag:
                raise RuntimeError(f"missing upload etag for part {index}")
            etags.append(etag)

    completed = request_data(
        session.post(
            COMPLETE_RESOURCE,
            data={
                "in_boss_key": meta["in_boss_key"],
                "resource_id": meta["resource_id"],
                "etags": ",".join(etags),
                "upload_id": meta["upload_id"],
                "model_id": 7,
            },
            headers=HEADERS,
            timeout=60,
        )
    )
    return str(completed["download_url"])


def create_task(session: Any, download_url: str) -> str:
    data = request_data(
        session.post(
            CREATE_TASK,
            json={
                "resource": download_url,
                "model_id": "7",
            },
            headers=HEADERS,
            timeout=60,
        )
    )
    return str(data["task_id"])


def wait_result(
    session: Any,
    task_id: str,
    poll_interval: float,
    timeout: float,
    on_poll: Callable[[], None] | None = None,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        data = request_data(
            session.get(
                TASK_RESULT,
                params={
                    "model_id": 7,
                    "task_id": task_id,
                },
                headers=HEADERS,
                timeout=60,
            )
        )
        state = int(data.get("state", -1))

        if state == 4:
            result = data.get("result")
            return json.loads(result) if isinstance(result, str) else result
        if state == 3:
            remark = data.get("remark") or ""
            raise RuntimeError(f"bijian asr failed: {remark}")

        if on_poll:
            on_poll()

        time.sleep(poll_interval)

    raise TimeoutError(f"bijian asr timeout: {task_id}")


def result_to_segments(result: dict[str, Any]) -> list[Segment]:
    segments = []
    for item in result.get("utterances", []):
        text = clean_text(str(item.get("transcript") or item.get("text") or ""))
        if not text:
            continue
        start_ms = int(item.get("start_time") or item.get("start") or 0)
        end_ms = int(item.get("end_time") or item.get("end") or start_ms)
        segments.append(Segment(start_ms, end_ms, text))
    return segments


def _ms_to_hms(ms: int) -> tuple[int, int, int, int]:
    return ms // 3_600_000, ms // 60_000 % 60, ms // 1_000 % 60, ms % 1_000


def srt_time(ms: int) -> str:
    h, m, s, ms_ = _ms_to_hms(ms)
    return f"{h:02d}:{m:02d}:{s:02d},{ms_:03d}"


def compact_time(ms: int) -> str:
    h, m, s, _ = _ms_to_hms(ms)
    if h:
        return f"[{h:02d}:{m:02d}:{s:02d}]"
    return f"[{m:02d}:{s:02d}]"


def write_outputs(out_dir: Path, stem: str, segments: list[Segment]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    srt = out_dir / f"{stem}.srt"
    txt = out_dir / f"{stem}.txt"
    jsonl = out_dir / f"{stem}.jsonl"

    srt_lines = []
    for index, segment in enumerate(segments, 1):
        srt_lines.extend(
            [
                str(index),
                f"{srt_time(segment.start_ms)} --> {srt_time(segment.end_ms)}",
                segment.text,
                "",
            ]
        )
    srt.write_text("\n".join(srt_lines), encoding="utf-8")

    txt_lines = [
        f"{compact_time(segment.start_ms)}{segment.text}" for segment in segments
    ]
    txt.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")

    with jsonl.open("w", encoding="utf-8") as file:
        for index, segment in enumerate(segments, 1):
            file.write(
                json.dumps(
                    {
                        "index": index,
                        "start_ms": segment.start_ms,
                        "end_ms": segment.end_ms,
                        "start": round(segment.start_ms / 1000, 3),
                        "end": round(segment.end_ms / 1000, 3),
                        "text": segment.text,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )


def output_stem(video: Path) -> str:
    stem = video.stem
    for source in RECORDING_PREFIXES:
        course_prefix = f"{source}_{video.parent.name}_"
        if stem.startswith(course_prefix):
            return stem[len(course_prefix):]
    alternation = "|".join(RECORDING_PREFIXES)
    return re.sub(rf"^(?:{alternation})_[^_]+_", "", stem, count=1)


def check_output_name_collisions(videos: list[Path]) -> None:
    seen: dict[str, Path] = {}
    collisions = []
    for video in videos:
        stem = output_stem(video)
        previous = seen.get(stem)
        if previous:
            collisions.append((stem, previous, video))
        else:
            seen[stem] = video

    if not collisions:
        return

    lines = ["Output name collision after stripping recording prefixes:"]
    for stem, first, second in collisions:
        lines.extend(
            [
                f"  {stem}",
                f"    {first}",
                f"    {second}",
            ]
        )
    raise SystemExit("\n".join(lines))


def natural_sort_key(path: Path) -> list[tuple[int, int | str]]:
    parts = re.split(r"(\d+)", str(path).casefold())
    return [(1, int(part)) if part.isdigit() else (0, part) for part in parts]


def collect_videos(paths: list[str], recursive: bool) -> list[Path]:
    videos = []
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_dir():
            pattern = "**/*" if recursive else "*"
            videos.extend(
                p for p in path.glob(pattern)
                if p.is_file() and p.suffix.lower() in VIDEO_EXTS
            )
        elif path.is_file() and path.suffix.lower() in VIDEO_EXTS:
            videos.append(path)
    return sorted(set(videos), key=natural_sort_key)


def default_output_dir(videos: list[Path]) -> Path:
    video_dirs = {video.parent.resolve() for video in videos}
    if len(video_dirs) == 1:
        return video_dirs.pop() / "transcripts"
    return Path.cwd() / "transcripts"


def transcribe_video(
    session: Any,
    video: Path,
    out_dir: Path,
    overwrite: bool,
    poll_interval: float,
    timeout: float,
    index: int,
    total: int,
    retries: int,
) -> str:
    stem = output_stem(video)
    prefix = f"[{index}/{total}] {stem}"
    if not overwrite and all((out_dir / f"{stem}.{ext}").exists() for ext in ("srt", "txt", "jsonl")):
        print(f"{prefix}  skip")
        return "skip"

    try:
        audio = out_dir / "audio" / f"{stem}.mp3"
        _with_elapsed(f"{prefix}  audio", lambda: run_ffmpeg(video, audio, overwrite))

        _begin(f"{prefix}  upload ")

        def on_upload(part: int, n_parts: int) -> None:
            _tick(f"[{part}/{n_parts}]")

        download_url = upload_audio(session, audio, on_progress=on_upload)

        def on_submit_retry(attempt: int, delay: float) -> None:
            _print(f"{prefix}  submit retry {attempt}/{retries - 1} in {delay:.0f}s")

        _print(f"{prefix}  submit")
        task_id = _retry(
            create_task, session, download_url,
            retries=retries,
            on_retry=on_submit_retry,
        )

        _begin(f"{prefix}  asr ")
        asr_start = time.monotonic()

        def on_poll() -> None:
            _tick(f"{int(time.monotonic() - asr_start)}s")

        result = wait_result(session, task_id, poll_interval, timeout, on_poll=on_poll)
        segments = result_to_segments(result)
        if not segments:
            _print(f"{prefix}  EMPTY", "\n")
            return "empty"

        write_outputs(out_dir, stem, segments)
        _print(f"{prefix}  OK", "\n")
        return "ok"

    except Exception as exc:
        _print(f"{prefix}  FAIL  {exc}", "\n")
        return "fail"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Batch transcribe course mp4 files with direct Bijian/BCut ASR.",
    )
    parser.add_argument(
        "inputs", nargs="+", help="mp4 file(s) or directory/directories"
    )
    parser.add_argument("-o", "--output-dir")
    parser.add_argument("-r", "--recursive", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--poll-interval", type=float, default=2)
    parser.add_argument("--timeout", type=float, default=7200)
    parser.add_argument(
        "--retries", type=int, default=3,
        help="max attempts for transient API errors (default: 3)",
    )
    args = parser.parse_args()

    try:
        import requests
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency: requests. Install it with `python -m pip install requests`."
        ) from exc

    videos = collect_videos(args.inputs, args.recursive)
    if not videos:
        raise SystemExit("No mp4 files found.")
    check_output_name_collisions(videos)
    if not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg not found in PATH.")

    out_dir = Path(args.output_dir) if args.output_dir else default_output_dir(videos)
    session = requests.Session()

    labels = {"ok": "OK", "skip": "skipped", "empty": "empty", "fail": "failed"}
    counts: dict[str, int] = {key: 0 for key in labels}
    total = len(videos)
    for i, video in enumerate(videos, 1):
        result = transcribe_video(
            session,
            video,
            out_dir,
            args.overwrite,
            args.poll_interval,
            args.timeout,
            index=i,
            total=total,
            retries=args.retries,
        )
        counts[result] += 1

    parts = [f"{counts[k]} {v}" for k, v in labels.items() if counts[k]]
    print(f"done: {total} files ({', '.join(parts)})")

    return 1 if counts["fail"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
