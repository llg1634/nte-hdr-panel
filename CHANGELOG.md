# 更新日志

## 0.1.1

- 重做 WebUI：改为 macOS 设置风格，左侧导航、右侧设置分组，降低渐变和大装饰元素。
- 保留浅色和深色两套主题，移动端改为单列设置页。
- 补齐 GitHub-ready 文档：中英文 README、快速使用、原理说明、备份恢复、上传指南、常见问题和发布检查清单。
- 统一中文发布名为“异环原生 HDR 一键开启工具”，短名“异环 HDR 面板”，英文名“NTE HDR Panel”。
- 补充搜索关键词矩阵、仓库描述、GitHub Topics 建议、参考项目致谢和链接引用。
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
