# 项目开发约定

## 文风

- `README.md` 和本文件使用中文；`SKILL.md` 和 `references/` 使用简洁的英文，笔记模板保持中文。
- 每个正文段落写在同一物理行，让显示工具自动换行。
- 以唯一版本口吻描述完整功能，文档与当前实现保持同步。
- 用正向、直接的表述说明行为和用途，段落在内容完整处自然结束。
- 目录与文件名称简短、直观，工作区结构以 `SKILL.md` 为准。
- 文档各管一件事，同一内容只写一处：README 写安装和产品决策，`SKILL.md` 写 Agent 的命令与流程，`references/files.md` 写文件格式，`references/notes.md` 写笔记模板，本文件写开发约束与代码结构。
- `.claude-plugin/` 和 `agents/openai.yaml` 是 Claude Code 和 Codex 的安装元数据，描述与 `SKILL.md` 保持一致。

## 实现范围

- 平台集成范围为课程元数据、视频、字幕和 PPT 截图。
- 功能按输入输出解耦，文档说明能力与必要依赖，调用顺序和组合由 Agent 根据任务决定。脚本承担省事的机械处理，如拼图和相似分组，采用简单默认值与显式选项。
- 命令行统一在 `scripts/yanhekit.py`，依赖集中写在它的 PEP 723 头部；其余模块只提供函数，新功能以子命令加入。
- 模块分工：`client.py` 会话、API 和校园网直连，`auth.py` 统一身份认证，`download.py` 资源下载与 `course.json`，`server.py` 本地页面后端与下载队列，`transcribe.py` BCut 转录，`transcript.py` 课次文件路径与时间轴的检索、导出和字幕封装，`slides.py` 拼图、相似检测和 PDF。
- 脚本在各平台和 Harness 中直接可用：文本读写显式指定 UTF-8，需要用户打开的地址打印到输出。
- 命令输出供 Agent 和人阅读：每项一行，从属内容缩进，课次内的路径相对课次目录，不输出 JSON。
- 工作区结构、产物路径和笔记模板固定遵循 `SKILL.md` 与 `references/`；Agent 在该框架内选择工具、分析方式和内容深度。
- 改动保持精小，采用单一实现路径；辅助函数以实际复用和清晰职责为依据。优先使用成熟库，如 tenacity、m3u8、img2pdf 和 Pillow。
- 验证限于改动涉及的实际行为，测试与校验以功能必需为准。
- 登录交互和凭证处理完整收敛在本地 UI 与后端。
- Agent 结合课程上下文、PPT 和音频完成转录的语义修订。

## 本地 UI

- 本地页面是快速操作和查看下载情况的辅助窗口，能力以命令行为准，页面只做选择和展示。后端用 Flask，状态经 SSE 推送；`/api/` 校验 Host 和启动时生成的 token。
- 前端源码在 `ui/`：React、Tailwind CSS v4、shadcn/ui（Mira）、Radix 和 motion。`components/ui/` 只保留用到的 shadcn 组件，并按 bit-autologin 的样式剪裁。
- `app.tsx` 订阅状态并协调操作，`api.ts` 收敛请求和 SSE，`login.tsx`、`course.tsx` 各自管理视图与交互，共用控件放在 `controls.tsx`。构建产物在 `scripts/ui/`，随 SKILL 发布。
- 界面文字和页面上的错误提示用自然、简练的中文，用于操作和状态反馈；命令行输出和帮助用英文。开关位于文字右侧；设置行由图标块、标题、一行说明和右侧控件组成。
- 图标使用 Lucide，线宽 1.5px，跟随所在文字字号。密码显隐的斜线从左上向右下绘制，历时 280ms；深浅色切换在太阳和月亮之间旋转缩放。
- 按钮的加载圈从左侧滑入，文字保持居中；发送、验证、冷却和下载统一通过状态控制加载与禁用样式。
- 输入框和验证码框复用 shadcn 焦点环；验证码框使用中性灰底和上下方向的轻微内阴影。
- 登录卡片的高度由 `useHeight` 测量并过渡，各步骤横向滑动；首次状态到达后显示页面，动画用于后续状态切换。
- 下载行参照 macOS 下载列表：细进度条、一行状态文字，右侧是暂停/继续/重试和取消两个圆形小按钮。

## 命令

- 前端开发：在 `ui/` 运行 `pnpm dev`，再用 `YANHEKIT_DEV=http://localhost:5173 uv run scripts/yanhekit.py ui` 启动后端，Vite 把 `/api` 代理到 5174 并提供热更新。
- 前端提交前运行 `pnpm format` 和 `pnpm check`，再用 `pnpm build` 把静态产物输出到 `scripts/ui/`。
- Python 使用 `uvx ruff format scripts` 和 `uvx ruff check scripts`，风格由 `ruff.toml` 规定。
