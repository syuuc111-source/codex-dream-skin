---
name: codex-dream-skin
description: 为 Windows Codex 桌面应用应用、启动、验证、修复、更新或恢复完整装饰皮肤。当用户需要超出官方颜色设置的 Codex 主题、粉紫色 Dream/Fiona 风格界面、更新后重新应用皮肤，或需要不修改 WindowsApps 和 app.asar 的安全恢复方式时使用。
---

# Codex 梦幻皮肤

通过 Chromium DevTools Protocol（CDP）向渲染器注入可恢复的皮肤，启动的仍是 Microsoft Store 安装的官方 Codex 程序。不得替换 WindowsApps 中的文件，也不得取得其所有权。

这是上游 Windows 技能的中文翻译。英文原文见 `SKILL.en.md`。脚本名、参数、目录和技术标识保持原样。

## 工作流程

1. 准备 Node.js 22 或更新版本，关闭 Codex，然后运行一次 `scripts/install-dream-skin.ps1`。安装器保留原生外观设置，初始化主题，将运行文件复制到 `%LOCALAPPDATA%\CodexDreamSkin\engine`，并创建不依赖源码目录的启动、恢复和托盘快捷方式。上游技能原文称默认主题为桥本有菜；实际发行版可能使用不同预设，应以下载版本的资源为准。
2. 使用 `Codex Dream Skin` 快捷方式，或运行 `%LOCALAPPDATA%\CodexDreamSkin\engine\scripts\start-dream-skin.ps1`。快捷方式在重启已打开的 Codex 前询问；命令行调用必须显式添加 `-RestartExisting`。
3. 启动后执行 `scripts/verify-dream-skin.ps1 -ScreenshotPath <绝对路径>`。连续背景、首页框架、原生输入框、侧栏图层或注入标记任一缺失，都应判定失败。原生建议卡片数量随窗口尺寸变化，可能为两到四个。
4. 添加完整主题包时，使用托盘的“导入主题 ZIP…”。仅接受普通 `.zip`。正式 Studio 包包含 `manifest.json`、非空 `theme.json`、通过本地校验的非空 `theme.css`、恰好一张登记的背景图，以及可选许可证或签名文件。可信的本地简化包必须恰好包含 `theme.json`、`theme.css` 及其引用图片。导入只加入主题库，不更改当前主题；也可手动将完整三文件目录放入主题目录。以前保存的不含 CSS 的旧主题仍可切换，但不会注入额外 CSS。
5. 兼容的 DreamSkin.cc 主题可使用 Setup.exe 注册的 `dreamskin://apply?version=ver_...` 链接。处理器只能从固定 API 获取已批准元数据及 ZIP，要求 `applyCompatible: true`，显示原生确认窗口，校验字节数与 SHA-256，再复用严格的导入流程。不接受任意 URL、路径、命令或静默应用参数。
6. 按 `references/qa-inventory.md` 检查截图。验收前必须检查首页及普通聊天任务页。
7. 运行 `scripts/restore-dream-skin.ps1`，移除当前皮肤、关闭保存的 CDP 会话，并正常重新打开 Codex。`-RestoreBaseTheme` 只恢复已保存外观键；`-RecoverConfigBackup` 用于明确要求的损坏配置逐字节恢复；`-Uninstall` 删除快捷方式。配置恢复完成后会归档本次安装的备份，下次安装重新记录基线。

## 约束与注意事项

- 保留官方可执行文件、包签名、聊天、宠物、插件及认证状态。
- 主题图片必须是不含界面的纯壁纸，不得导入 README 截图、假窗口、侧栏、卡片、输入框、徽标或已烘焙文字。
- 一张连续的 16:9 壁纸覆盖整个窗口；侧栏、主区、标题和输入框共同承担文字可读性。首页可突出氛围，任务页应减少干扰。
- `appearance: auto` 优先跟随原生计算得到的 `color-scheme`，系统外观仅作后备。图片亮度可调整颜色和构图，不得因此切换用户的外观模式；显式 `light`、`dark` 始终优先。
- “选择项目”样式必须附着在真实项目选择器工具栏上，当前项目按钮保持可点击，不得画一个脱离原控件的替代品。
- 装饰图层使用 `pointer-events: none`，真实按钮、导航和输入框保持在其上方。
- Codex 更新后重新安装并启动；脚本动态发现当前 Appx 包。保存的路径只有仍匹配已注册包身份时，才能用于进程控制。
- Windows 启动优先使用清单派生的包激活入口，并将远程调试参数与 Chromium 136+ 所需的持久、非默认托管 CDP 配置目录配套使用。仅在可见进程参数证明 owl 将 CDP 参数编码进 `codex://` 时，才允许尝试准确的 Store `app\ChatGPT.exe` 后备入口，且必须经过 `common-windows.ps1` 的包身份与路径检查。回滚时保留启动前 PID 集合。访问被拒绝，或原始参数存在却未验证到监听器时，必须停止。后备入口仅用于诊断，不能当作 owl 兼容性证明；不得更改 WindowsApps ACL 来强行运行。
- 默认端口 `9335` 被占用时，默认启动器寻找空闲端口；显式指定的端口被占用则直接失败。
- 保持注入守护进程运行，以支持页面导航与重新加载。状态和日志位于 `%LOCALAPPDATA%\CodexDreamSkin`。
- 监听器为已连接渲染器注册经过代次检查的提前注入载荷，使页面重新加载或导航时尽早绘制皮肤；不支持的 CDP 目标安全回退。
- 当前主题、主题库、导入图片、暂停标记和托盘控制均位于 `%LOCALAPPDATA%\CodexDreamSkin`。复制或编码前拒绝空文件及超过 10 MB 的图片。
- 主题包不支持 `.dreamskin`；拒绝路径穿越、链接或重解析项、嵌套归档、不明确的根目录、Windows 保留路径、超出大小或数量限制及不符合主题和图片规则的包。
- 社区深链接只接受规范版本 ID。更改当前主题前，拒绝重定向、未批准或不兼容元数据、ID 不匹配、非布尔兼容字段、不安全显示信息、意外媒体类型、字节或哈希不匹配，以及并发应用。
- 托管存储写入时，检查路径中每个已存在部分，拒绝目录联接和其他重解析点。导入前使用随包 Node 元数据解析器，拒绝尺寸超过 16384 像素或总像素超过 5000 万的图片。
- CDP 目标必须使用同端口的回环 WebSocket，归属当前 Store 包，保留启动时 Browser ID，并暴露预期的 Codex 渲染器标记。
- 回环绑定避免局域网访问，但 CDP 不提供同一用户进程间的认证。启用期间仅运行可信本地程序；不再使用时通过恢复操作关闭调试会话。
- `config.toml` 必须保持严格 UTF-8。不得用依赖系统编码的 PowerShell 整文件读写、静默转换 UTF-16，或覆盖读取后被别人修改的文件。遇到不明确的 TOML 结构时，应在写入前失败，而非猜测改写。
- 安装、启动、恢复及验证使用 `common-windows.ps1` 中的单用户操作锁串行执行。
- `%LOCALAPPDATA%\CodexDreamSkin\engine` 是安装器管理的运行目录。重新安装前退出 Dream Skin 托盘，使安装器能原子替换目录，并将全部快捷方式更新到同一副本。
- 已安装快捷方式与托盘子进程使用 `RemoteSigned`，不得使用 `Bypass`。只在暂存的托管 `.ps1` 副本与所选源文件的字节哈希一致后，清除这些副本的互联网区域标记；不得修改用户持久执行策略或覆盖组策略。

## 验证命令

```powershell
powershell -NoProfile -File tests\run-tests.ps1
node --check scripts\injector.mjs
node --check assets\renderer-inject.js
```

## 配套资源

- `scripts/injector.mjs`：CDP 连接、渲染器注入、验证、截屏与移除。
- `scripts/common-windows.ps1`：Store 包发现、Node 校验、托管运行目录安装、端口归属、状态及进程身份检查。
- `scripts/config-utf8.ps1`：原子 UTF-8 配置备份、选择性恢复与显式恢复。
- `assets/dream-skin.css`：完整视觉图层。
- `assets/renderer-inject.js`：幂等 DOM 接入与清理。
- `assets/dream-reference.jpg`：默认纯背景图；上游原文描述为 2560×1440 桥本有菜壁纸，不含 Codex 界面。
- `assets/theme.json`：默认预设的自适应主题契约。
- `scripts/theme-windows.ps1`：当前主题与已保存主题的持久化、安全图片导入、暂停状态及预设初始化。
- `scripts/apply-community-theme.ps1`：固定来源的社区下载、原生确认、完整性校验、严格 ZIP 导入、应用与回滚编排。
- `scripts/tray-dream-skin.ps1`：Windows Forms 托盘，提供应用、暂停、导入、保存、切换和完整恢复。
- `references/qa-inventory.md`：功能与视觉验收清单。
- `references/runtime-notes.md`：故障排查与更新行为。
- `tests/run-tests.ps1`：运行目录、配置、状态、恢复、载荷与 CDP 校验回归检查；`-EngineOnly` 检查运行目录脱离源码后的独立性。
