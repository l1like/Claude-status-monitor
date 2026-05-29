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

### 方式一：下载 exe（无需 Python）

从 [Releases](https://github.com/l1like/Claude-status-monitor/releases) 下载 `monitor.exe` 和 `update_status.exe`，放到同一目录下。

1. 双击 `monitor.exe` 启动托盘图标
2. 在 `~/.claude/settings.json` 中配置 hooks（见[配置](#配置)），命令路径指向 `update_status.exe` 的实际位置

### 方式二：从源码运行

```bash
pip install -r requirements.txt
python monitor.py
```

或双击 `start_monitor.bat`（后台静默启动，无控制台窗口）。

托盘图标右键 → **Quit** 退出。

### 打包为 exe

```bash
pip install pyinstaller
pyinstaller --onefile --windowed monitor.py
pyinstaller --onefile update_status.py
# 产物在 dist/ 目录
```

## 工作原理

```
Claude Code hooks  →  update_status.exe  →  status.json  →  monitor.exe  →  托盘图标
```

1. **update_status** — CLI 工具，写入状态到 `status.json`
2. **monitor** — 托盘程序，每 500ms 轮询 `status.json`，更新图标颜色
3. **Claude Code hooks** — 在 `~/.claude/settings.json` 中配置，自动调用 `update_status`

## 配置

在用户级 `~/.claude/settings.json` 中添加以下 hooks，**注意替换路径**：

```json
"hooks": {
  "SessionStart": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "C:/path/to/status-monitor/update_status.exe done"
        }
      ]
    }
  ],
  "UserPromptSubmit": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "C:/path/to/status-monitor/update_status.exe running"
        }
      ]
    }
  ],
  "Stop": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "C:/path/to/status-monitor/update_status.exe done"
        }
      ]
    }
  ],
  "PostToolUse": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "C:/path/to/status-monitor/update_status.exe running"
        }
      ]
    }
  ],
  "PermissionRequest": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "C:/path/to/status-monitor/update_status.exe confirm"
        }
      ]
    }
  ],
  "PostToolUseFailure": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "C:/path/to/status-monitor/update_status.exe error"
        }
      ]
    }
  ]
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
