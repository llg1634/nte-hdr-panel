# 更新日志

## 0.1.3

- 新增独立产品功能“恢复未配置 HDR 的原版”。
- 后端会自动识别最早一份未配置 HDR 的 `Engine.ini` 备份，并作为固定原版回退目标。
- WebUI 新增原版候选信息卡和独立按钮，不再要求用户手动从备份列表里猜哪一份才是原版。
- README、中英文文档和 FAQ 同步补充“原版回退”语义说明。
- 本地发版脚本改为同时生成 onedir zip 和单文件 exe。

## 0.1.2

- 修正致谢方向：重点补充 DLSSTweaks、RenoDX、ReShade、Special K 等社区图形工具的引用与边界说明。
- 明确本项目不包含上述项目的二进制文件，不注入游戏进程，不修改游戏安装目录。
- 在 README、README.en、NOTICE、ACKNOWLEDGEMENTS、docs/07、FAQ 和 Release notes 模板中同步说明。

## 0.1.1

- 重做 WebUI：改为 macOS 设置风格，左侧导航、右侧设置分组，降低渐变和大装饰元素。
- 保留浅色和深色两套主题，移动端改为单列设置页。
- 补齐 GitHub-ready 文档：中英文 README、快速使用、原理说明、备份恢复、上传指南、常见问题和发布检查清单。
- 统一中文发布名为“异环原生 HDR 一键开启工具”，短名“异环 HDR 面板”，英文名“NTE HDR Panel”。
- 补充搜索关键词矩阵、仓库描述、GitHub Topics 建议、相关社区工具引用与区分、参考项目致谢和链接引用。
- 补充 DLSSTweaks、RenoDX、ReShade、Special K 的致谢与边界说明。
- 新增 `CONTRIBUTING.md`、`SECURITY.md`、`NOTICE.md`、`LICENSE`、`.gitattributes`、`.gitignore`。
- 新增 GitHub Actions Windows 构建 workflow。
- 新增发布说明模板和本地 release 打包脚本。

## 0.1.0

- 新增本机 WebUI，默认监听 `127.0.0.1:22533`，与 DLSS 面板的 `22532` 分开。
- 新增异环 `Engine.ini` 检测，默认路径为 `%LOCALAPPDATA%\HT\Saved\Config\Windows`。
- 新增 UE 原生 HDR 写入：`r.HDR.EnableHDROutput`、`r.HDR.UI.Level`、`r.HDR.Display.MaxLuminance`、`r.HDR.Display.MidLuminance`。
- 新增三组预设：UE 默认、偏亮、高亮屏。
- 新增写入前 manifest 备份和按清单恢复。
- 新增默认只读保护；本机实测不只读会被游戏启动阶段重写，只读后配置可保留。
- 新增 NVIDIA DLSS HUD 状态检测和开关，用于辅助确认 `DX12` / `HDR Mode: Custom`。
- 新增普通进程名检测；不读取游戏模块，避免触发“黑客工具”误报。
- 新增“退出工具”按钮，避免只关闭网页后本地后端继续运行。
- README 补充原理、参数含义、修改范围、反作弊误报排查和备份恢复逻辑。
