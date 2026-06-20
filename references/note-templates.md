# Note Templates

Templates for lecture notes and the course-level summary. Load this file only when generating or updating notes.

Naming and placement:

- Single lecture note: `<course-name>/notes/<lecture-stem>.md`, where `<lecture-stem>` removes the leading `(camera|screen)_<course-name>_` from the video stem (e.g. `第10周_星期一_第4大节`).
- Course-level summary: `<course-name>/课程总结.md`.
- Do not create a single-lecture note for white-noise-only or empty-class recordings. Mention them only in the course summary.
- If a category is absent, write `无`.
- Mark uncertain ASR spans as `需确认` with timestamps instead of guessing.

## Single Lecture Markdown

```markdown
# 第X周 星期X 第X大节

- 视频：`<video>.mp4`
- 字幕：`transcripts/<subtitle>.srt`

## 时间轴

- `00:00:00` 主题或问题：一句话说明为什么值得回看
- `00:00:00` 主题或问题：一句话说明为什么值得回看

## 关键点

### 考勤/签到/小测

### 作业

### 考试/复习重点

### 其他需要回看的片段

## 省流

- 用少量要点概括本节主线、关键概念、例题或证明位置。
- 保留术语和时间戳，避免完整复述。
```

## Course Markdown (课程总结)

Maintain one course-level Markdown that serves as the review dashboard and index to lecture notes:

```markdown
# <course-name> 课程总结

## 复习优先

### 考试/复习重点

### 作业

### 考勤/签到/小测

### 其他

## 课程索引

| 课次 | 笔记 | 视频 | 点名 | 作业 | 考试 | 概述 |
| --- | --- | --- | --- | --- | --- | --- |
| 第X周 星期X 第X大节 | `<note>.md`/无 | `<video>.mp4` | ''/'有' | ''/'有' | ''/'有' | 一句话概括，不加句号 |

## 课程内容

### 第X周 星期X 第X大节

- 时间点：`00:00:00` 主题；`00:00:00` 主题

概括本节主线、关键概念、例题或证明位置。

### 第X周 星期X 第X大节

- 时间点：`00:00:00` 主题；`00:00:00` 主题

概括本节主线、关键概念、例题或证明位置。
```

For incremental work on newly downloaded recordings, create notes only for new real lectures, then update the course summary in place so new material naturally joins the current review dashboard, index, assignments, exam hints, and content map. Avoid changelog-like wording such as "new transcription" unless the user explicitly asks for process notes.
