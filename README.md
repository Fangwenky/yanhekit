# yanhekit

延河课堂（aita.yanhekt.cn）课程资料 SKILL：下载回放视频、平台字幕和 PPT 截图，拼接 PDF，用 BCut 转录，再由 Agent 检索材料、整理笔记和回答课程问题。

## 安装

Claude Code：

```text
/plugin install yanhekit --marketplace windlandneko/yanhekit
```

Codex：克隆仓库后，把 `skills/yanhekit/` 目录复制到 `~/.codex/skills/yanhekit/`。

运行需要 [uv](https://docs.astral.sh/uv/) 和 PATH 中的 ffmpeg。没有 uv 时，用 Python 3.11+ 安装 `skills/yanhekit/scripts/yanhekit.py` 头部列出的包。

## 使用

在 Harness 里直接说需求，如“下载这门课本周的回放，整理笔记和作业”。Agent 按 `SKILL.md` 调用命令、读取产物并写笔记。想自己点选课次时，让 Agent 打开下载页面。

## 设计

- 能力各自独立：课程列表、资源下载、PPT 拼图与相似分组、BCut 转录、检索与导出，组合由 Agent 按任务决定。
- 脚本做鉴权、媒体签名、并发下载、格式转换，以及拼图、相似分组这类机械处理；挑选 PPT、修订术语、分析内容和写笔记由 Agent 结合转录、PPT 和音频完成。
- 登录在本地页面完成，Agent 不接触密码。会话 cookie 和学号存在 `~/.config/yanhekit/`，勾选“记住账户”时密码存入系统钥匙串。
- 联网命令在后台探测校园地址 `10.0.11.240`，证书校验通过后直连，下载速度从公网的约 20–30 MB/s 提到约 85 MB/s；探测不通时照常走公网。
- 下载页面是命令行的辅助窗口：按学期选课，勾选课次和内容，查看队列进度，并可暂停、继续、重试或取消。
- 工作区里直接打开看的成品用中文命名，脚本和 Agent 反复读写的材料用英文短名，中间文件集中在 `.cache/`。

## 文档

| 文件 | 内容 |
| --- | --- |
| `skills/yanhekit/SKILL.md` | Agent 使用说明：命令、工作区结构和工作流程 |
| `skills/yanhekit/references/files.md` | 工作区文件格式 |
| `skills/yanhekit/references/notes.md` | 笔记模板 |
| `AGENTS.md` | 开发约定与代码结构 |
