import tkinter as tk
from tkinter import messagebox, simpledialog
from tabulate import tabulate
from datetime import datetime, timedelta
import os

USER_FILE = "users.txt"
TASK_FILE = "study_tasks.txt"

class UserAuth:
    def __init__(self):
        self.current_user = None

    def sign_up(self, username, password):
        if os.path.exists(USER_FILE):
            with open(USER_FILE, "r") as file:
                users = dict(line.strip().split(",") for line in file.readlines())
        else:
            users = {}

        if username in users:
            messagebox.showerror("Error", "Username already exists!")
            return False
        
        with open(USER_FILE, "a") as file:
            file.write(f"{username},{password}\n")
        
        messagebox.showinfo("Success", "User registered successfully!")
        return True

    def login(self, username, password):
        if not os.path.exists(USER_FILE):
            messagebox.showerror("Error", "No users found. Please sign up first!")
            return False
        
        with open(USER_FILE, "r") as file:
            users = dict(line.strip().split(",") for line in file.readlines())

        if username in users and users[username] == password:
            self.current_user = username
            messagebox.showinfo("Success", "Login successful!")
            return True
        else:
            messagebox.showerror("Error", "Invalid username or password!")
            return False

    def logout(self):
        self.current_user = None
        messagebox.showinfo("Logout", "You have been logged out!")

class StudyTask:
    def __init__(self, subject, deadline, hours_required):
        self.subject = subject
        self.deadline = datetime.strptime(deadline, "%Y-%m-%d")
        self.hours_required = hours_required
        self.priority = None  

    def calculate_priority(self):
        days_left = (self.deadline - datetime.today()).days
        self.priority = max(1, 10 - days_left)

    def to_string(self):
        return f"{self.subject},{self.deadline.strftime('%Y-%m-%d')},{self.hours_required}"

    @staticmethod
    def from_string(task_str):
        subject, deadline, hours_required = task_str.split(",")
        return StudyTask(subject, deadline, int(hours_required))

class StudySchedule:
    def __init__(self):
        self.tasks = []
        self.load_tasks()

    def add_task(self, subject, deadline, hours_required):
        task = StudyTask(subject, deadline, hours_required)
        task.calculate_priority()
        self.tasks.append(task)
        self.save_tasks()

    def delete_task(self, subject):
        self.tasks = [task for task in self.tasks if task.subject != subject]
        self.save_tasks()
        messagebox.showinfo("Success", f"Task '{subject}' deleted successfully!")

    def generate_schedule(self, available_hours_per_day):
        self.load_tasks()  # Ensure tasks are loaded before generating schedule
        self.tasks.sort(key=lambda task: task.priority, reverse=True)

        schedule = []
        current_date = datetime.today()

        for task in self.tasks:
            study_days = (task.hours_required // available_hours_per_day) + (task.hours_required % available_hours_per_day > 0)
            for _ in range(study_days):
                allocated_hours = min(available_hours_per_day, task.hours_required)
                schedule.append([task.subject, current_date.strftime("%Y-%m-%d"), allocated_hours])
                task.hours_required -= allocated_hours
                if task.hours_required <= 0:
                    break
                current_date += timedelta(days=1)

        return schedule

    def show_tasks(self):
        self.load_tasks()  # Ensure latest tasks are displayed
        if not self.tasks:
            messagebox.showinfo("Study Tasks", "No study tasks available!")
            return
        
        task_list = [[task.subject, task.deadline.strftime("%Y-%m-%d"), task.hours_required] for task in self.tasks]
        result = tabulate(task_list, headers=["Subject", "Deadline", "Hours Required"], tablefmt="grid")
        messagebox.showinfo("Study Tasks", result)

    def save_tasks(self):
        with open(TASK_FILE, "w") as file:
            for task in self.tasks:
                file.write(task.to_string() + "\n")

    def load_tasks(self):
        self.tasks = []  # Clear the list before loading
        if os.path.exists(TASK_FILE):
            with open(TASK_FILE, "r") as file:
                self.tasks = [StudyTask.from_string(line.strip()) for line in file.readlines()]

class StudyPlannerApp:
    def __init__(self, root):
        self.auth = UserAuth()
        self.current_user = None  
        self.root = root
        self.root.title("AI Study Planner")
        self.create_login_ui()

    def create_login_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="AI Study Planner", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Username:").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        tk.Label(self.root, text="Password:").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        tk.Button(self.root, text="Login", command=self.login).pack(pady=5)
        tk.Button(self.root, text="Sign Up", command=self.sign_up).pack()
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if self.auth.login(username, password):
            self.current_user = username  
            self.create_main_ui()

    def sign_up(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if self.auth.sign_up(username, password):
            self.current_user = username  
            self.create_main_ui()

    def create_main_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text=f"Welcome, {self.current_user}!", font=("Arial", 14)).pack(pady=10)

        tk.Label(self.root, text="Available study hours per day:").pack()
        self.hours_entry = tk.Entry(self.root)
        self.hours_entry.pack()

        tk.Button(self.root, text="Add Study Task", command=self.add_task).pack(pady=5)
        tk.Button(self.root, text="Show Study Tasks", command=self.show_tasks).pack(pady=5)
        tk.Button(self.root, text="Show Study Plan", command=self.show_schedule).pack()
        tk.Button(self.root, text="Delete Study Task", command=self.delete_task).pack(pady=5)
        tk.Button(self.root, text="Logout", command=self.logout).pack(pady=10)

        self.schedule = StudySchedule()

    def add_task(self):
        subject = simpledialog.askstring("Input", "Enter subject:")
        deadline = simpledialog.askstring("Input", "Enter deadline (YYYY-MM-DD):")
        hours_required = simpledialog.askinteger("Input", "Enter required study hours:")

        if subject and deadline and hours_required:
            self.schedule.add_task(subject, deadline, hours_required)
            messagebox.showinfo("Success", "Task added successfully!")

    def delete_task(self):
        subject = simpledialog.askstring("Input", "Enter subject to delete:")
        if subject:
            self.schedule.delete_task(subject)

    def show_tasks(self):
        self.schedule.show_tasks()

    def show_schedule(self):
        available_hours = int(self.hours_entry.get()) if self.hours_entry.get().isdigit() else 0
        schedule = self.schedule.generate_schedule(available_hours)
        
        if schedule:
            result = tabulate(schedule, headers=["Subject", "Date", "Hours Allocated"], tablefmt="grid")
            messagebox.showinfo("Study Plan", result)
        else:
            messagebox.showinfo("No Schedule", "No study tasks available!")

    def logout(self):
        self.auth.logout()
        self.current_user = None  
        self.create_login_ui()

if __name__ == "__main__":
    root = tk.Tk()
    app = StudyPlannerApp(root)
    root.mainloop()
