# Changelog

## v1.0.0 (2026-05-29)

- 系统托盘彩色圆点图标，实时显示 Claude Code 会话状态
- 五种状态：done（绿）、running（黄）、confirm（橙）、error（红）、idle（灰）
- running 和 confirm 状态带正弦波呼吸灯动画
- 每 500ms 轮询 status.json，低资源占用
- 双击 start_monitor.bat 后台静默启动，无控制台窗口
- 右键菜单支持开机自启（写入注册表 Run 键）
- 右键菜单退出，自动清理 PID 文件
- 打包为独立 exe，无需 Python 环境
- Claude Code hooks 自动调用 update_status 切换状态
