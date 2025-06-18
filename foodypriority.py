import psutil
import requests
import time
import json
import os
import tkinter as tk
from tkinter import messagebox
import sys

def is_already_running():
    current_pid = os.getpid()
    current_name = os.path.basename(sys.argv[0]).lower()

    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['pid'] != current_pid and proc.info['name'].lower() == current_name:
            return True
    return False

if is_already_running():
    sys.exit()  # exit silently if already running

CONFIG_FILE = "config.json"

# map config priority names to the psutil names
PRIORITY_MAP = {
    "idle": psutil.IDLE_PRIORITY_CLASS,
    "below_normal": psutil.BELOW_NORMAL_PRIORITY_CLASS,
    "normal": psutil.NORMAL_PRIORITY_CLASS,
    "above_normal": psutil.ABOVE_NORMAL_PRIORITY_CLASS,
    "high": psutil.HIGH_PRIORITY_CLASS,
    "realtime": psutil.REALTIME_PRIORITY_CLASS
}

# default config in case config.json doesn't exist or is malformed
default_config = {
    "apps": [
        {"name": "geometrydash.exe", "priority": "high"},
        {"name": "discord.exe", "priority": "idle"}
    ],
    "scan_interval": 5
}

# update notifs
CURRENT_VERSION = "1.1.0"  # update this with actual app version

def notify_update(latest_version):
    root = tk.Tk()
    root.withdraw()  # hide main window
    messagebox.showinfo("Update Available", f"A new version {latest_version} is available!")
    root.destroy()

def check_for_update():
    try:
        response = requests.get("https://api.github.com/repos/Foodynooby/foodys-priority-manager/releases/latest")
        response.raise_for_status()
        latest_version = response.json()['tag_name']
        if latest_version != CURRENT_VERSION:
            notify_update(latest_version)
    except Exception as e:
        print(f"Update check failed: {e}")

# config ts
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("warning: config.json is malformed, loading defaults.")
    return default_config

# the functioning part of this
def set_priorities(apps):
    for proc in psutil.process_iter(['name']):
        try:
            proc_name = proc.info['name'].lower()
            for app in apps:
                if app["name"].lower() in proc_name:
                    desired_priority = PRIORITY_MAP.get(app["priority"], psutil.NORMAL_PRIORITY_CLASS)
                    if proc.nice() != desired_priority:
                        proc.nice(desired_priority)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

# scanning
def main():
    while True:
        check_for_update()
        config = load_config()
        apps = config.get("apps", [])
        interval = config.get("scan_interval", 5)

        set_priorities(apps)
        time.sleep(interval)

if __name__ == "__main__":
    main()

# crypto.mine(infinity times a million) hahaha i mined all ur crypto im crypto mining rn and ratting yuri_f4n's skyblock account specifically because i hate that thing
# im kidding these hashtags mean theyre just comments XD April Fools
