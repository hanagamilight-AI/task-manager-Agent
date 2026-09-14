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

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      AI TASK AGENT SYSTEM                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   User       │◄──►│  TaskAgent   │◄──►│  Scheduler   │       │
│  │  Interface   │    │   Core       │    │   Engine     │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│         │                   │                   │                │
│         │                   ▼                   │                │
│         │            ┌──────────────┐          │                │
│         │            │   Task       │          │                │
│         │            │   Manager    │          │                │
│         │            └──────────────┘          │                │
│         │                   │                   │                │
│         ▼                   ▼                   ▼                │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              tasks.json (Persistent Storage)             │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Component Architecture

#### 1. **TaskAgent Class** (Core Controller)
The main orchestrator that coordinates all components.

**Responsibilities:**
- Initialize and manage task data
- Coordinate between user input, scheduler, and storage
- Handle daily reset logic
- Manage agent lifecycle (start/stop)

**Key Methods:**
- `__init__()`: Initialize agent and load tasks
- `start()`: Launch interactive mode with background scheduler
- `reset_daily_tasks()`: Clear tasks for new day

#### 2. **User Interface Module** (Interactive Layer)
Handles all user interactions through CLI.

**Responsibilities:**
- Display menus and prompts
- Collect task input (name, deadline)
- Show task lists and reminders
- Process user commands

**Commands Supported:**
- `a/add`: Add new task
- `v/view`: Display all tasks
- `c/complete`: Mark task complete
- `r/remind`: Trigger immediate reminder
- `q/quit/exit`: Exit agent

#### 3. **Scheduler Engine** (Time-Based Automation)
Background thread that runs continuously for automated reminders.

**Responsibilities:**
- Monitor system time every 60 seconds
- Trigger 9 AM morning check-in
- Execute bi-hourly reminders (10, 12, 14, 16, 18, 20, 22)
- Prevent duplicate reminders per hour

**Schedule:**
```
09:00 → Morning task collection
10:00 → Reminder check
12:00 → Reminder check
14:00 → Reminder check
16:00 → Reminder check
18:00 → Reminder check
20:00 → Reminder check
22:00 → Reminder check
```

#### 4. **Task Manager** (Business Logic)
Handles task operations and urgency calculations.

**Responsibilities:**
- Add tasks with deadline parsing
- Calculate time until deadline
- Filter tasks due within 2-hour window
- Sort by urgency
- Mark tasks as complete

**Urgency Levels:**
- 🚨 OVERDUE: Deadline passed
- ⚠️ Minutes left: < 1 hour remaining
- ⏳ Hours remaining: 1-2 hours left

#### 5. **Data Persistence Layer** (Storage)
JSON-based file storage for task data.

**File Structure (`tasks.json`):**
```json
{
  "date": "2024-01-15",
  "daily_tasks": [
    {
      "id": 1,
      "name": "Finish project report",
      "deadline": "2024-01-15 17:00",
      "deadline_display": "17:00",
      "completed": false,
      "created_at": "2024-01-15 09:30:45"
    }
  ]
}
```

**Operations:**
- `load_tasks()`: Read from JSON file on startup
- `save_tasks()`: Write to JSON file after modifications
- Auto-create file if not exists

### Data Flow

```
User Input → TaskAgent.add_task() → Task Validation → 
JSON Storage → Scheduler Monitor → Time Check → 
Reminder Trigger → Urgency Calculation → User Notification
```

### Threading Model

```
Main Thread (Interactive CLI)
    │
    ├── User Command Loop (blocking I/O)
    │
    └── Background Scheduler Thread (daemon)
            │
            └── While running:
                    - Sleep 60s
                    - Check time conditions
                    - Trigger reminders if needed
```

### Time Handling Logic

1. **Daily Reset**: Compare current date with stored date
2. **Morning Check**: Trigger at hour == 9 on new days
3. **Bi-hourly Reminders**: Trigger when `hour % 2 == 0` and hour ∈ [10,22]
4. **Deadline Parsing**: Convert HH:MM to datetime with today's date
5. **Overnight Deadlines**: If deadline < now, assume tomorrow

### Error Handling

- Invalid time formats caught with ValueError
- Missing task IDs handled gracefully
- File I/O errors managed with Path.exists() checks
- Thread safety via sequential JSON operations

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
