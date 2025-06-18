import tkinter as tk
from tkinter import messagebox
import json
import winreg
import os


# Priorities mapping
PRIORITY_OPTIONS = ["low", "below normal", "normal", "above normal", "high", "REALTIME!!! (a lil risky)"]
PRIORITY_MAP = {
    "low": "idle",
    "below normal": "below_normal",
    "normal": "normal",
    "above normal": "above_normal",
    "high": "high",
    "REALTIME!!! (a lil risky)": "realtime"
}

CONFIG_FILE = "config.json"

DEFAULT_APPS = [
    {"name": "discord.exe", "priority": "low"},
    {"name": "geometrydash.exe", "priority": "high"}
]

def set_autostart(enabled: bool):
    app_name = "foodypriority"
    exe_path = os.path.abspath("foodypriority.exe")

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        if enabled:
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
        else:
            winreg.DeleteValue(key, app_name)
        winreg.CloseKey(key)
    except FileNotFoundError:
        pass
    except PermissionError:
        print("permission denied :( try running as administrator?")

class AppEntry(tk.Frame):
    def __init__(self, master, name="", priority="normal", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.app_name = tk.Entry(self, width=20)
        self.app_name.insert(0, name)
        self.app_name.pack(side=tk.LEFT, padx=5)

        self.priority = tk.StringVar(value=priority)
        self.priority_menu = tk.OptionMenu(self, self.priority, *PRIORITY_OPTIONS)
        self.priority_menu.pack(side=tk.LEFT, padx=5)

        self.remove_button = tk.Button(self, text="❌", command=self.destroy)
        self.remove_button.pack(side=tk.LEFT, padx=5)

    def get_data(self):
        return {
            "name": self.app_name.get().strip(),
            "priority": PRIORITY_MAP[self.priority.get()]
        }

class ConfigApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("foody's priority config :3")
        self.geometry("400x500")

        self.autostart_var = tk.BooleanVar()
        self.autostart_checkbox = tk.Checkbutton(self, text="launch on bootup", variable=self.autostart_var, command=self.toggle_autostart)
        self.autostart_checkbox.pack(pady=5)

        self.entries_frame = tk.Frame(self)
        self.entries_frame.pack(pady=10)

        self.app_entries = []

        tk.Button(self, text="➕ add app", command=self.add_entry).pack(pady=5)

        tk.Label(self, text="scan interval (secs):").pack()
        self.scan_interval = tk.Entry(self)
        self.scan_interval.insert(0, "5")
        self.scan_interval.pack(pady=5)

        tk.Button(self, text="💾 save config", command=self.save_config).pack(pady=10)

        self.load_config()

    def toggle_autostart(self):
        set_autostart(self.autostart_var.get())

    def add_entry(self, name="", priority="normal"):
        entry = AppEntry(self.entries_frame, name, priority)
        entry.pack(pady=2)
        self.app_entries.append(entry)

    def save_config(self):
        apps = []
        for entry in self.app_entries:
            data = entry.get_data()
            if data["name"]:
                apps.append(data)

        config = {
            "auto_start": self.autostart_var.get(),
            "apps": apps,
            "scan_interval": int(self.scan_interval.get())
        }

        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)

        messagebox.showinfo("success!!", "configuration saved :3c")

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)

            self.autostart_var.set(config.get("auto_start", False))

            for app in config.get("apps", []):
                reverse_priority = next((k for k, v in PRIORITY_MAP.items() if v == app["priority"]), "normal")
                self.add_entry(app["name"], reverse_priority)

            self.scan_interval.delete(0, tk.END)
            self.scan_interval.insert(0, str(config.get("scan_interval", 5)))
        else:
            # First run — populate with defaults
            for app in DEFAULT_APPS:
                self.add_entry(app["name"], app["priority"])

if __name__ == "__main__":
    app = ConfigApp()
    app.mainloop()
