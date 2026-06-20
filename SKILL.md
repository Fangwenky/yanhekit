---
name: yanhekt-asr
description: Transcribe, convert, clean, analyze, and summarize Yanhekt/沿河课堂 and other course recording videos. Use when user needs to process lecture/class recordings, 课程录播, or classroom videos into transcripts, readable notes, chapter outlines, timestamped review maps, key points, assignments, exam hints, or course-level summaries.
version: 0.1.0
---

# Yanhekt(沿河课堂) Lecture Recording Workflow

Use the bundled direct Bijian/BCut script first for course recordings:

`scripts/bcut_batch_asr.py`

It calls the Bijian/BCut web ASR API directly, extracts audio with `ffmpeg`, and writes three files per video:

- `.srt`: video subtitles
- `.txt`: token-efficient agent reading format, e.g. `[12:34]字幕内容`
- `.jsonl`: script-friendly segments with `index`, `start_ms`, `end_ms`, `start`, `end`, `text`

## Pipeline

1. **Organize recordings** by course if needed.
2. **Transcribe** with the bundled script and preserve raw `.srt`, `.txt`, `.jsonl`.
3. **Check quality quickly**: inspect the start, middle, and end of `.txt`; mark white-noise/empty-class lessons instead of forcing summaries.
4. **Clean only when needed**: use raw `.txt` for fast indexing and review extraction; polish only key spans or final subtitles.
5. **Analyze from subtitles/transcripts**: extract chapters, concepts, definitions, examples, assignments, questions, and review points.
6. **Summarize conservatively**: do not invent content absent from subtitles.

## Scaling to many lectures

When a single request covers many lectures, do not read every full transcript into the main context. Dispatch read-only subagents to read in batches and report back, then write the notes yourself.

- Group lectures into batches of about three and give each batch to one subagent.
- Each subagent reads only its `.txt` (and `.jsonl`/`.srt` when needed) and returns a concise structured report per lecture.
- Read the returned reports, then generate the per-lecture `notes/<lecture-stem>.md` and update `课程总结.md` yourself, so formatting, voice, and conservative summarizing stay consistent across the course.

## Quick Start

The script is PEP 723 compatible but `uv` is better if available. If using plain Python and `requests` is missing:

```
python -m pip install requests
```

Batch transcribe one course directory:

```
python path/to/scripts/bcut_batch_asr.py ./<course-name>
```

Transcribe one video:

```
python path/to/scripts/bcut_batch_asr.py ./<course-name>/<video>.mp4
```

With `uv`, dependencies are installed from the script metadata:

```
uv run --script path/to/scripts/bcut_batch_asr.py ./<course-name>
```

Useful options:

```
# Recurse into subdirectories
python path/to/scripts/bcut_batch_asr.py ./<course-name> -r

# Choose output directory
python path/to/scripts/bcut_batch_asr.py ./<course-name> -o ./<course-name>/transcripts

# Re-run existing outputs
python path/to/scripts/bcut_batch_asr.py ./<course-name> --overwrite
```

Default output:

- If all inputs are in one video directory: `<video-dir>/transcripts/`
- If inputs span multiple directories: `./transcripts/`
- Temporary extracted audio: `<output-dir>/audio/`

## Notes

- Each class period is 45 minutes followed by a 5-minute break; recording starts exactly at class time, but may not stop exactly on time.
- Some recordings may contain only white noise like one-line outputs such as `12345` or repeated `head/eye/one two`: treat as empty-class.
- A class section usually spans two or three 45+5 periods, so expect white noise around the ~45-minute break, and maybe a second break later as well.
- Ignore empty-class lessons and short white-noise spans around breaks or at the end; focus on actual lecture content.
- Saved transcript and note stems should drop the recording prefix `(camera|screen)_<course-name>_`. For example, `camera_高等数学_第1周_星期一_第1大节` saves as `第1周_星期一_第1大节`.
- Common names the ASR often mishears: `乐学` is the on-campus learning platform; `i北理` is the campus app, a special version of `钉钉` (DingTalk). Map garbled spellings back to these.

## File Organization

Organize course recordings by course.

- Preserve video filenames and place them at `<course-name>/<video>.mp4`.
- Put script outputs under `<course-name>/transcripts/` by default: `<lecture-stem>.srt`, `<lecture-stem>.txt`, `<lecture-stem>.jsonl`.
- Define `<lecture-stem>` by removing the leading `(camera|screen)_<course-name>_` from the video stem, e.g. `第10周_星期一_第4大节`.
- For agent reading, prefer `<lecture-stem>.txt` before loading `.srt`; use `.jsonl` for scripts and timestamp math.
- Put each real lecture note under `<course-name>/notes/`.
- Keep the course-level summary at `<course-name>/课程总结.md`.

## Output

Generate one Markdown note for each real lecture, then maintain one course-level summary (`课程总结.md`) for the whole course.
Prioritize things easy to miss: attendance, assignments, deadlines, exam hints, teacher warnings, platform notices, and small procedural details.
Include course content only as a timestamped navigation map; do not rewrite the lecture as a full textbook or transcript.

For the exact note and course-summary templates, naming rules, and incremental-update guidance, see `references/note-templates.md`.

## Additional Resources

- `scripts/bcut_batch_asr.py` — batch ASR pipeline (ffmpeg audio extraction + Bijian/BCut API), writes `.srt`/`.txt`/`.jsonl` per video.
- `references/note-templates.md` — single-lecture and course-summary Markdown templates with naming and incremental-update rules.
