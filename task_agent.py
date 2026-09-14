#!/usr/bin/env python3
"""
AI Task Agent - Manages daily tasks with hourly reminders
- Asks for tasks at 9:00 AM
- Reminds about deadlines every 2 hours
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import time
import threading

class TaskAgent:
    def __init__(self, data_file="tasks.json"):
        self.data_file = Path(data_file)
        self.tasks = self.load_tasks()
        self.running = False
        
    def load_tasks(self):
        """Load tasks from JSON file"""
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {"daily_tasks": [], "date": None}
    
    def save_tasks(self):
        """Save tasks to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def reset_daily_tasks(self):
        """Reset tasks if it's a new day"""
        today = datetime.now().strftime("%Y-%m-%d")
        if self.tasks["date"] != today:
            print(f"\n📅 New day started: {today}")
            self.tasks = {"daily_tasks": [], "date": today}
            self.save_tasks()
            return True
        return False
    
    def add_task(self, task_name, deadline_str):
        """Add a new task with deadline"""
        try:
            # Parse deadline (accepts various formats)
            deadline = datetime.strptime(deadline_str, "%H:%M")
            deadline = deadline.replace(
                year=datetime.now().year,
                month=datetime.now().month,
                day=datetime.now().day
            )
            
            # If deadline has passed today, assume tomorrow
            if deadline < datetime.now():
                deadline += timedelta(days=1)
            
            task = {
                "id": len(self.tasks["daily_tasks"]) + 1,
                "name": task_name,
                "deadline": deadline.strftime("%Y-%m-%d %H:%M"),
                "deadline_display": deadline.strftime("%H:%M"),
                "completed": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.tasks["daily_tasks"].append(task)
            self.save_tasks()
            print(f"✅ Task added: '{task_name}' (Deadline: {deadline.strftime('%H:%M')})")
            return True
            
        except ValueError as e:
            print(f"❌ Invalid deadline format. Please use HH:MM (24-hour format). Error: {e}")
            return False
    
    def get_due_tasks(self):
        """Get tasks that are due or upcoming"""
        now = datetime.now()
        due_tasks = []
        
        for task in self.tasks["daily_tasks"]:
            if not task["completed"]:
                deadline = datetime.strptime(task["deadline"], "%Y-%m-%d %H:%M")
                # Include tasks due within the next 2 hours or already overdue
                time_until_deadline = (deadline - now).total_seconds() / 3600
                if time_until_deadline <= 2:
                    due_tasks.append({
                        **task,
                        "hours_until_deadline": time_until_deadline
                    })
        
        return sorted(due_tasks, key=lambda x: x["hours_until_deadline"])
    
    def display_tasks(self):
        """Display all current tasks"""
        print("\n" + "="*60)
        print("📋 YOUR DAILY TASKS")
        print("="*60)
        
        if not self.tasks["daily_tasks"]:
            print("No tasks for today yet!")
        else:
            for task in self.tasks["daily_tasks"]:
                status = "✓" if task["completed"] else "○"
                print(f"[{status}] Task #{task['id']}: {task['name']}")
                print(f"    Deadline: {task['deadline_display']} | Created: {task['created_at']}")
        
        print("="*60 + "\n")
    
    def send_reminder(self):
        """Send reminder for upcoming deadlines"""
        due_tasks = self.get_due_tasks()
        
        if due_tasks:
            print("\n" + "🔔"*20)
            print("⏰ REMINDER - Upcoming Deadlines!")
            print("🔔"*20)
            
            for task in due_tasks:
                hours_left = task["hours_until_deadline"]
                if hours_left < 0:
                    urgency = "🚨 OVERDUE!"
                elif hours_left < 1:
                    minutes_left = int(hours_left * 60)
                    urgency = f"⚠️ Only {minutes_left} minutes left!"
                else:
                    urgency = f"⏳ {hours_left:.1f} hours remaining"
                
                print(f"\n{urgency}")
                print(f"   Task: {task['name']}")
                print(f"   Deadline: {task['deadline_display']}")
            
            print("\n" + "🔔"*20 + "\n")
        else:
            print("✅ No upcoming deadlines in the next 2 hours!")
    
    def ask_for_tasks(self):
        """Interactive prompt to collect tasks from user"""
        print("\n" + "🤖"*20)
        print("Good morning! I'm your AI Task Agent.")
        print("Let's plan your day together.")
        print("🤖"*20 + "\n")
        
        while True:
            task_name = input("Enter a task (or 'done' to finish): ").strip()
            
            if task_name.lower() in ['done', 'exit', 'quit']:
                break
            
            if not task_name:
                continue
            
            deadline = input(f"  Deadline for '{task_name}' (HH:MM, 24h format): ").strip()
            
            if deadline:
                self.add_task(task_name, deadline)
        
        print("\nGreat! Your tasks are set. I'll remind you every 2 hours.")
        self.display_tasks()
    
    def mark_complete(self, task_id):
        """Mark a task as completed"""
        for task in self.tasks["daily_tasks"]:
            if task["id"] == task_id:
                task["completed"] = True
                self.save_tasks()
                print(f"✅ Marked task '{task['name']}' as complete!")
                return True
        print(f"❌ Task #{task_id} not found.")
        return False
    
    def run_scheduler(self):
        """Run the background scheduler for reminders"""
        print("\n🕐 Starting reminder scheduler...")
        print("Press Ctrl+C to stop\n")
        
        last_reminder_hour = -1
        last_morning_check_date = None
        
        while self.running:
            now = datetime.now()
            current_hour = now.hour
            
            # Reset tasks for new day
            if now.strftime("%Y-%m-%d") != last_morning_check_date:
                if self.reset_daily_tasks():
                    # Ask for tasks at 9 AM on new days
                    if current_hour >= 9:
                        self.ask_for_tasks()
                last_morning_check_date = now.strftime("%Y-%m-%d")
            
            # Morning task collection at 9 AM
            if current_hour == 9 and last_morning_check_date == now.strftime("%Y-%m-%d"):
                if not self.tasks["daily_tasks"]:
                    print("\n⏰ It's 9 AM! Time to set up your daily tasks.")
                    self.ask_for_tasks()
                last_morning_check_date = None  # Reset to prevent repeated prompts
            
            # Reminder every 2 hours (at even hours: 10, 12, 14, 16, 18, 20, 22)
            if current_hour % 2 == 0 and current_hour != last_reminder_hour:
                if current_hour >= 10 and current_hour <= 22:
                    self.send_reminder()
                    last_reminder_hour = current_hour
            
            # Check every minute
            time.sleep(60)
    
    def start(self, interactive=True):
        """Start the agent"""
        self.running = True
        self.reset_daily_tasks()
        
        if interactive:
            # Check if it's after 9 AM and no tasks exist
            now = datetime.now()
            if now.hour >= 9 and not self.tasks["daily_tasks"]:
                print("⏰ Looks like you haven't set up today's tasks yet!")
                response = input("Would you like to add tasks now? (y/n): ").strip().lower()
                if response == 'y':
                    self.ask_for_tasks()
            
            self.display_tasks()
            
            # Start scheduler in background thread
            scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
            scheduler_thread.start()
            
            # Interactive command loop
            while self.running:
                print("\nCommands: [a]dd task | [v]iew tasks | [c]omplete task | [r]emind now | [q]uit")
                cmd = input("> ").strip().lower()
                
                if cmd in ['q', 'quit', 'exit']:
                    self.running = False
                    print("👋 Goodbye! Stay productive!")
                    break
                elif cmd in ['a', 'add']:
                    task_name = input("Task name: ").strip()
                    deadline = input("Deadline (HH:MM): ").strip()
                    self.add_task(task_name, deadline)
                elif cmd in ['v', 'view']:
                    self.display_tasks()
                elif cmd in ['c', 'complete']:
                    task_id = input("Task ID to complete: ").strip()
                    if task_id.isdigit():
                        self.mark_complete(int(task_id))
                elif cmd in ['r', 'remind']:
                    self.send_reminder()
                else:
                    print("Unknown command. Try again.")
        else:
            # Non-interactive mode (for background service)
            self.run_scheduler()


def main():
    """Main entry point"""
    print("\n" + "🤖"*20)
    print("   AI TASK AGENT - Daily Task Manager")
    print("🤖"*20)
    print("\nFeatures:")
    print("  • Asks for tasks at 9:00 AM")
    print("  • Reminds you of deadlines every 2 hours")
    print("  • Tracks task completion")
    print("  • Persists tasks across sessions")
    print("\nStarting agent...\n")
    
    agent = TaskAgent()
    agent.start(interactive=True)


if __name__ == "__main__":
    main()
