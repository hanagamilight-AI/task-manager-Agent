# AI Task Agent

A Python-based AI agent that manages your daily tasks with automated reminders.

## Features

- 🌅 **Morning Check-in**: Automatically asks for your tasks at 9:00 AM
- ⏰ **Bi-hourly Reminders**: Reminds you of upcoming deadlines every 2 hours (10 AM, 12 PM, 2 PM, 4 PM, 6 PM, 8 PM, 10 PM)
- 📝 **Task Management**: Add, view, and mark tasks as complete
- 💾 **Persistent Storage**: Tasks are saved to JSON and persist across sessions
- 🔄 **Daily Reset**: Automatically resets tasks each new day

## Installation

No external dependencies required! Just Python 3.6+.

```bash
cd /workspace
python3 task_agent.py
```

## Usage

### Interactive Mode (Default)

When you run the agent, it will:
1. Check if it's a new day and reset tasks if needed
2. If it's after 9 AM and no tasks exist, prompt you to add tasks
3. Start the background reminder scheduler
4. Provide an interactive command loop

**Available Commands:**
- `a` or `add` - Add a new task
- `v` or `view` - View all tasks
- `c` or `complete` - Mark a task as complete
- `r` or `remind` - Trigger an immediate reminder check
- `q` or `quit` or `exit` - Exit the agent

### Example Session

```
🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖
   AI TASK AGENT - Daily Task Manager
🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖

Commands: [a]dd task | [v]iew tasks | [c]omplete task | [r]emind now | [q]uit
> a
Task name: Finish project report
Deadline (HH:MM): 17:00
✅ Task added: 'Finish project report' (Deadline: 17:00)

> v
============================================================
📋 YOUR DAILY TASKS
============================================================
[○] Task #1: Finish project report
    Deadline: 17:00 | Created: 2026-09-14 10:30:45
============================================================

> c
Task ID to complete: 1
✅ Marked task 'Finish project report' as complete!
```

## How It Works

1. **9 AM Task Collection**: The agent checks at 9 AM if you have tasks. If not, it prompts you to enter them with their deadlines.

2. **Every 2 Hours Reminder**: At even hours (10, 12, 14, 16, 18, 20, 22), the agent checks for tasks due within the next 2 hours and sends reminders with urgency levels:
   - 🚨 OVERDUE! - Deadline has passed
   - ⚠️ Only X minutes left! - Less than 1 hour remaining
   - ⏳ X.X hours remaining - Between 1-2 hours left

3. **Data Persistence**: All tasks are stored in `tasks.json` in the same directory.

## Files

- `task_agent.py` - Main agent script
- `tasks.json` - Auto-generated file storing your daily tasks

## Customization

You can modify these values in the code:
- Reminder frequency (currently every 2 hours)
- Morning check-in time (currently 9 AM)
- Reminder window (currently shows tasks due within 2 hours)

## License

MIT License - Feel free to modify and use as needed!
