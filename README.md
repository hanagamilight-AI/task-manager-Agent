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

## Deployment Options

### 🖥️ Desktop/Laptop (Recommended)
Perfect for running while you work at your computer.

```bash
python3 task_agent.py
```

**Pros:** Full terminal experience, easy to modify, no battery concerns
**Cons:** Only works when computer is on and script is running

### 📱 Mobile Deployment

While this agent is designed for terminal environments, here are your options for mobile use:

#### Option 1: Termux (Android) - Most Direct
Run the Python script directly on Android using Termux.

**Steps:**
1. Install **Termux** from F-Droid or Play Store
2. Open Termux and run:
   ```bash
   pkg update && pkg upgrade
   pkg install python
   ```
3. Transfer `task_agent.py` to your phone (via git clone, scp, or manual copy)
4. Run:
   ```bash
   python task_agent.py
   ```

**Limitations:**
- Terminal must stay open for reminders to work
- Battery optimization may kill the process
- No notifications when app is closed

---

#### Option 2: Cloud Server + Telegram (RECOMMENDED) ✅

This version runs 24/7 on a cloud server and sends notifications directly to your phone via Telegram.

**Files Created:**
- `task_agent_telegram.py` - Telegram-integrated agent
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variables template

**Setup Instructions:**

**Step 1: Create Telegram Bot**
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow prompts to name your bot (e.g., "MyTaskAgent")
4. **Save the API Token** (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

**Step 2: Get Your Chat ID**
1. Search for `@userinfobot` in Telegram
2. Start the bot and it will reply with your Chat ID
3. **Save your Chat ID** (looks like: `123456789`)

**Step 3: Choose Cloud Platform (Free Options)**

**A. Replit (Easiest)**
```bash
# 1. Create account at https://replit.com
# 2. Create new Python repl
# 3. Upload task_agent_telegram.py and requirements.txt
# 4. Add Secrets (Environment Variables):
#    - TELEGRAM_BOT_TOKEN = your_bot_token
#    - TELEGRAM_CHAT_ID = your_chat_id
# 5. Click "Run"
# 6. Use "Always On" feature (requires Hacker plan) or use uptime robot
```

**B. Render.com (Free Tier)**
```bash
# 1. Create account at https://render.com
# 2. Create new "Web Service"
# 3. Connect your GitHub repo
# 4. Set environment variables in dashboard
# 5. Deploy!
```

**C. Railway.app (Free Tier)**
```bash
# 1. Create account at https://railway.app
# 2. New Project → Deploy from GitHub
# 3. Add environment variables
# 4. Deploy
```

**D. Google Cloud Run / AWS Lambda / Azure Functions**
- More complex but generous free tiers
- Requires containerization or serverless setup

**Step 4: Configure Environment Variables**
```bash
# On your cloud platform, set:
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

**Step 5: Test It Locally First**
```bash
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"
pip install -r requirements.txt
python task_agent_telegram.py
```

You should receive a startup message on Telegram!

**How It Works:**
- **9:00 AM**: Bot messages you asking for today's tasks
- **You Reply**: Send tasks in format: `Task Name - HH:MM`
- **10 AM, 12 PM, 2 PM, 4 PM, 6 PM, 8 PM, 10 PM**: Automatic reminders
- **10:00 PM**: Daily summary of completed vs pending tasks

**Example Interaction:**
```
Bot (9:00 AM):
☀️ Good Morning! It's 9:00 AM.
📝 What are your tasks for today?

You:
Team meeting - 10:00
Submit report - 14:30
Call client - 16:00
Gym - 18:00

Bot:
✅ Task Added!
📌 Team meeting
⏰ Deadline: 10:00 AM

Bot (10:00 AM Reminder):
⏰ Reminder - 10:00 AM

🚨 OVERDUE:
• Team meeting - Due: 10:00 AM
  🚨 OVERDUE!

📋 UPCOMING:
• Submit report - Due: 2:30 PM
• Call client - Due: 4:00 PM
• Gym - Due: 6:00 PM
```

**Advantages:**
✅ Works 24/7 even when your phone is off
✅ Real push notifications
✅ No battery drain on your phone
✅ Free hosting options available
✅ Accessible from any device with Telegram

**Keep It Running 24/7:**
- **Replit**: Use UptimeRobot (free) to ping every 5 minutes
- **Render/Railway**: Automatically stay alive on free tier
- **GitHub Actions**: Schedule workflow to restart daily (advanced)

#### Option 3: Convert to Mobile App (Advanced)
Rebuild as a native mobile application.

**Technologies:**
- **React Native** / **Flutter** - Cross-platform
- **Swift** (iOS) / **Kotlin** (Android) - Native
- Use local notifications APIs for reminders

**Pros:** Best user experience, native notifications, background execution
**Cons:** Significant rewrite required, not just deploying existing code

#### Option 4: iOS Shortcuts + Cloud Script
For iPhone users who want minimal setup.

1. Host `task_agent.py` logic on a cloud function (AWS Lambda, Google Cloud Functions)
2. Create an iOS Shortcut that:
   - Calls the cloud function via HTTP
   - Displays results as notifications
3. Set up automation to run hourly

**Pros:** No app development, uses native iOS features
**Cons:** Limited interactivity, requires iCloud/Shortcuts setup

### 🔧 Quick Mobile Adaptation Guide

To make the current script more mobile-friendly with minimal changes:

1. **Add a simple HTTP API** using Flask:
   ```bash
   pip install flask
   ```

2. **Modify `task_agent.py`** to expose endpoints:
   ```python
   from flask import Flask, request, jsonify
   app = Flask(__name__)
   
   @app.route('/add_task', methods=['POST'])
   def add_task():
       # Add task logic
       return jsonify({"status": "success"})
   
   @app.route('/tasks', methods=['GET'])
   def get_tasks():
       # Return tasks as JSON
       return jsonify(agent.tasks)
   ```

3. **Deploy to a free tier** (Replit, Glitch, Render)

4. **Access via phone browser** or create simple curl commands in Shortcuts/Termux

### ⚠️ Important Considerations for Mobile

| Challenge | Solution |
|-----------|----------|
| Background execution | Use server-based approach or native app |
| Battery drain | Avoid running Python continuously on phone |
| No notifications | Integrate push notification service |
| Terminal closed = no reminders | Deploy to always-on server |
| Data persistence | Use cloud storage or sync to JSON file |

### Recommended Approach

**For most users:** Deploy to a free cloud server + Telegram bot integration. This gives you:
- ✅ 24/7 operation
- ✅ Real push notifications
- ✅ No battery impact on phone
- ✅ Access from any device
- ✅ Minimal code changes (~50 lines)

Would you like me to provide the complete Telegram integration code for this approach?

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
