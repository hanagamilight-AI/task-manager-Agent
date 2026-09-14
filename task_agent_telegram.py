"""
AI Task Agent with Telegram Integration
Runs on cloud server, sends reminders via Telegram bot
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import time
import requests
from telegram import Bot
from telegram.error import TelegramError

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TASKS_FILE = 'tasks.json'
LOG_FILE = 'task_agent.log'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Handles all Telegram bot communications"""
    
    def __init__(self, token: str, chat_id: str):
        if not token or not chat_id:
            raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set")
        
        self.bot = Bot(token=token)
        self.chat_id = chat_id
        
    def send_message(self, message: str, parse_mode: str = 'Markdown') -> bool:
        """Send a message to the user"""
        try:
            self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            logger.info(f"Message sent: {message[:50]}...")
            return True
        except TelegramError as e:
            logger.error(f"Telegram error: {e}")
            return False
    
    def send_morning_greeting(self) -> bool:
        """Send 9 AM morning greeting and ask for tasks"""
        message = (
            "☀️ *Good Morning!* It's 9:00 AM.\n\n"
            "📝 *What are your tasks for today?*\n\n"
            "Please reply with your tasks in this format:\n"
            "`Task Name - HH:MM` (24-hour format)\n\n"
            "*Examples:*\n"
            "`Team meeting - 10:00`\n"
            "`Submit report - 14:30`\n"
            "`Call client - 16:00`\n\n"
            "You can add multiple tasks, one per line."
        )
        return self.send_message(message)
    
    def send_reminder(self, tasks: List[Dict]) -> bool:
        """Send bi-hourly reminder with task status"""
        if not tasks:
            return True
            
        now = datetime.now()
        message = f"⏰ *Reminder - {now.strftime('%I:%M %p')}*\n\n"
        
        urgent_tasks = []
        upcoming_tasks = []
        overdue_tasks = []
        
        for task in tasks:
            if task.get('completed'):
                continue
                
            deadline_str = task['deadline']
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M')
            time_left = deadline - now
            
            task_info = f"• *{task['name']}* - Due: {deadline.strftime('%I:%M %p')}"
            
            if time_left.total_seconds() < 0:
                overdue_tasks.append(f"{task_info}\n  🚨 *OVERDUE!*")
            elif time_left.total_seconds() < 3600:  # Less than 1 hour
                minutes = int(time_left.total_seconds() / 60)
                urgent_tasks.append(f"{task_info}\n  ⚠️ Only {minutes} minutes left!")
            elif time_left.total_seconds() < 7200:  # Less than 2 hours
                hours = int(time_left.total_seconds() / 3600)
                upcoming_tasks.append(f"{task_info}\n  ⏳ {hours} hour(s) remaining")
            else:
                upcoming_tasks.append(task_info)
        
        if overdue_tasks:
            message += "*🚨 OVERDUE:*\n" + "\n".join(overdue_tasks) + "\n\n"
        if urgent_tasks:
            message += "*⚠️ URGENT:*\n" + "\n".join(urgent_tasks) + "\n\n"
        if upcoming_tasks:
            message += "*📋 UPCOMING:*\n" + "\n".join(upcoming_tasks) + "\n\n"
        
        if not overdue_tasks and not urgent_tasks and not upcoming_tasks:
            message += "✅ No pending tasks!\n\n"
        
        message += "_Next reminder in 2 hours._"
        
        return self.send_message(message)
    
    def send_task_confirmation(self, task_name: str, deadline: str) -> bool:
        """Confirm task addition"""
        deadline_dt = datetime.strptime(deadline, '%Y-%m-%d %H:%M')
        message = (
            f"✅ *Task Added!*\n\n"
            f"📌 *{task_name}*\n"
            f"⏰ Deadline: {deadline_dt.strftime('%I:%M %p')}\n\n"
            "I'll remind you every 2 hours!"
        )
        return self.send_message(message)
    
    def send_daily_summary(self, tasks: List[Dict]) -> bool:
        """Send end-of-day summary at 10 PM"""
        completed = sum(1 for t in tasks if t.get('completed'))
        pending = len(tasks) - completed
        
        message = (
            f"🌙 *Daily Summary - {datetime.now().strftime('%B %d, %Y')}*\n\n"
            f"✅ Completed: {completed}\n"
            f"⏳ Pending: {pending}\n\n"
        )
        
        if pending > 0:
            message += "_Unfinished tasks will carry over to tomorrow._"
        else:
            message += "🎉 Great job! All tasks completed!"
        
        return self.send_message(message)


class TaskManager:
    """Manages task storage and operations"""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.tasks: List[Dict] = []
        self.load_tasks()
    
    def load_tasks(self):
        """Load tasks from JSON file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    self.tasks = data.get('tasks', [])
                    last_date = data.get('last_date', '')
                    
                    # Check if it's a new day
                    today = datetime.now().strftime('%Y-%m-%d')
                    if last_date != today:
                        logger.info(f"New day detected ({today}), resetting tasks")
                        self.tasks = []
                        self.save_tasks()
            except json.JSONDecodeError:
                logger.error("Invalid JSON in tasks file")
                self.tasks = []
        else:
            logger.info("Tasks file not found, creating new one")
            self.save_tasks()
    
    def save_tasks(self):
        """Save tasks to JSON file"""
        data = {
            'tasks': self.tasks,
            'last_date': datetime.now().strftime('%Y-%m-%d')
        }
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved {len(self.tasks)} tasks")
    
    def add_task(self, name: str, deadline_str: str) -> Optional[Dict]:
        """Add a new task"""
        try:
            # Parse deadline time
            today = datetime.now().date()
            deadline_time = datetime.strptime(deadline_str, '%H:%M').time()
            deadline = datetime.combine(today, deadline_time)
            
            # If deadline is in the past, assume it's for tomorrow
            if deadline < datetime.now():
                deadline += timedelta(days=1)
            
            task = {
                'id': len(self.tasks) + 1,
                'name': name.strip(),
                'deadline': deadline.strftime('%Y-%m-%d %H:%M'),
                'completed': False,
                'created_at': datetime.now().isoformat()
            }
            
            self.tasks.append(task)
            self.save_tasks()
            logger.info(f"Added task: {name}")
            return task
            
        except ValueError as e:
            logger.error(f"Invalid deadline format: {e}")
            return None
    
    def mark_complete(self, task_id: int) -> bool:
        """Mark a task as complete"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['completed'] = True
                self.save_tasks()
                logger.info(f"Marked task {task_id} as complete")
                return True
        return False
    
    def get_pending_tasks(self) -> List[Dict]:
        """Get all pending (not completed) tasks"""
        return [t for t in self.tasks if not t.get('completed')]
    
    def get_all_tasks(self) -> List[Dict]:
        """Get all tasks"""
        return self.tasks


class TaskAgent:
    """Main AI Agent coordinating everything"""
    
    def __init__(self):
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            raise ValueError(
                "Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables.\n"
                "See README.md for setup instructions."
            )
        
        self.notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        self.task_manager = TaskManager(TASKS_FILE)
        self.running = False
        self.scheduler_thread = None
    
    def parse_user_tasks(self, message: str) -> List[tuple]:
        """Parse user's task list from message"""
        tasks = []
        lines = message.strip().split('\n')
        
        for line in lines:
            if '-' in line:
                parts = line.split('-')
                if len(parts) >= 2:
                    task_name = '-'.join(parts[:-1]).strip()
                    deadline = parts[-1].strip()
                    tasks.append((task_name, deadline))
        
        return tasks
    
    def handle_morning_checkin(self):
        """Handle 9 AM morning check-in"""
        logger.info("Sending morning check-in")
        self.notifier.send_morning_greeting()
    
    def handle_user_response(self, message: str):
        """Process user's task list response"""
        tasks = self.parse_user_tasks(message)
        
        if not tasks:
            self.notifier.send_message(
                "❌ I couldn't understand the tasks. Please use the format:\n"
                "`Task Name - HH:MM`\n\n"
                "Example: `Team meeting - 10:00`"
            )
            return
        
        added_count = 0
        for task_name, deadline in tasks:
            result = self.task_manager.add_task(task_name, deadline)
            if result:
                added_count += 1
                self.notifier.send_task_confirmation(task_name, deadline)
        
        if added_count > 0:
            self.notifier.send_message(
                f"✅ Successfully added {added_count} task(s)!\n\n"
                f"I'll remind you every 2 hours until your deadlines."
            )
    
    def send_bi_hourly_reminder(self):
        """Send reminder about pending tasks"""
        pending = self.task_manager.get_pending_tasks()
        
        if pending:
            self.notifier.send_reminder(pending)
        else:
            now = datetime.now()
            if now.hour >= 9:  # Only after morning check-in
                self.notifier.send_message(
                    f"⏰ *Reminder - {now.strftime('%I:%M %p')}*\n\n"
                    "✅ No pending tasks! Enjoy your day! 🎉\n\n"
                    "_Next reminder in 2 hours._"
                )
    
    def run_scheduler(self):
        """Background scheduler loop"""
        logger.info("Scheduler started")
        last_morning_check = None
        last_daily_summary = None
        
        while self.running:
            try:
                now = datetime.now()
                current_hour = now.hour
                current_minute = now.minute
                
                # Morning check-in at 9:00 AM
                if current_hour == 9 and current_minute == 0:
                    today = now.strftime('%Y-%m-%d')
                    if last_morning_check != today:
                        self.handle_morning_checkin()
                        last_morning_check = today
                
                # Bi-hourly reminders (10, 12, 14, 16, 18, 20, 22)
                if current_hour in [10, 12, 14, 16, 18, 20, 22] and current_minute == 0:
                    self.send_bi_hourly_reminder()
                
                # Daily summary at 22:00 (10 PM)
                if current_hour == 22 and current_minute == 0:
                    today = now.strftime('%Y-%m-%d')
                    if last_daily_summary != today:
                        tasks = self.task_manager.get_all_tasks()
                        self.notifier.send_daily_summary(tasks)
                        last_daily_summary = today
                
                # Sleep for 30 seconds to avoid excessive CPU usage
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)  # Wait longer on error
    
    def start(self):
        """Start the agent"""
        logger.info("Starting Task Agent...")
        self.running = True
        
        # Send startup notification
        self.notifier.send_message(
            "🤖 *Task Agent Started!*\n\n"
            "I'm now running and will:\n"
            "• Ask for tasks at 9:00 AM\n"
            "• Remind you every 2 hours\n"
            "• Send daily summary at 10:00 PM\n\n"
            "_Running on cloud server 24/7_"
        )
        
        # Start scheduler in background thread
        self.scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("Task Agent is running. Press Ctrl+C to stop.")
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the agent"""
        logger.info("Stopping Task Agent...")
        self.running = False
        self.notifier.send_message("🛑 Task Agent stopped.")


def main():
    """Entry point"""
    try:
        agent = TaskAgent()
        agent.start()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print("\n❌ Error: Missing configuration!")
        print("Please set the following environment variables:")
        print("  - TELEGRAM_BOT_TOKEN")
        print("  - TELEGRAM_CHAT_ID")
        print("\nSee README.md for setup instructions.\n")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == '__main__':
    main()
