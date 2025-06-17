import psutil
import time

# dictionary of app names and their desired priority levels
target_apps = {
    "geometrydash.exe": psutil.HIGH_PRIORITY_CLASS,
    "discord.exe": psutil.IDLE_PRIORITY_CLASS # this means low
}

# code to make it run constantly
while True:
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc_name = proc.info['name'].lower()
            for target_name, priority in target_apps.items():
                if target_name.lower() in proc_name:
                    current_priority = proc.nice()
                    if current_priority != priority:
                        proc.nice(priority)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass # yeah idk what this means i didnt write any of this lolol

    time.sleep(5)  # checks every 5 seconds
