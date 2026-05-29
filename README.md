# Claude Status Monitor

系统托盘图标，实时显示 Claude Code 会话状态。

## 效果

| 状态 | 颜色 | 动画 | 含义 |
|---|---|---|---|
| `done` | 🟢 绿色 | 无 | 空闲 / 任务完成 |
| `running` | 🟡 黄色 | 呼吸灯 | 正在执行 |
| `confirm` | 🟠 橙色 | 呼吸灯 | 需要手动确认 |
| `error` | 🔴 红色 | 无 | 工具执行出错 |

## 快速开始

```bash
pip install -r requirements.txt
python monitor.py
```

或双击 `start_monitor.bat`（后台静默启动，无控制台窗口）。

托盘图标右键 → **Quit** 退出。

## 工作原理

```
Claude Code hooks  →  update_status.py  →  status.json  →  monitor.py  →  托盘图标
```

1. **update_status.py** — CLI 脚本，写入状态到 `status.json`
2. **monitor.py** — 托盘程序，每 500ms 轮询 `status.json`，更新图标颜色
3. **Claude Code hooks** — 在 `~/.claude/settings.json` 中配置，自动调用 `update_status.py`

## 配置

Hooks 配置在用户级 `~/.claude/settings.json`，全局生效：

```json
"hooks": {
  "SessionStart":          → done     (启动/空闲)
  "UserPromptSubmit":      → running  (收到消息)
  "Stop":                  → done     (响应结束)
  "PostToolUse":           → running  (工具执行完，恢复运行)
  "PermissionRequest":     → confirm  (需要手动确认)
  "PostToolUseFailure":    → error    (工具出错)
}
```

## 文件结构

```
status-monitor/
├── monitor.py           # 托盘图标主程序
├── update_status.py     # 状态更新 CLI
├── status.json          # 当前状态（运行时生成）
├── monitor.pid          # 进程 PID（防止重复启动）
├── requirements.txt     # pystray, Pillow
├── start_monitor.bat    # 后台启动脚本
└── README.md
```
