import os
import time
import shutil
import base64
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import openai  # ensure openai is installed in your venv

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")  # set in environment for security

# Base directories
BASE_DIR         = os.path.dirname(os.path.abspath(__file__))
WATCH_FOLDER     = os.path.join(BASE_DIR, "watchFolder")
PROCESSED_FOLDER = os.path.join(BASE_DIR, "processedImg")

# Ensure folders exist
os.makedirs(WATCH_FOLDER,     exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def process_license_plate(image_path):
    """Uses OpenAI Vision API to extract license plate and state"""
    file_ts  = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    data_ts  = datetime.now().strftime("%Y/%m/%d_%H:%M:%S")

    with open(image_path, "rb") as img_file:
        b64 = base64.b64encode(img_file.read()).decode('utf-8')

    # Step 1: extract plate number
    resp_plate = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You extract only license plate numbers."},
            {"role": "user", "content": [
                {"type": "text", "text": "Extract only the license plate number."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
            ]}
        ],
        max_tokens=50
    )

    plate = None
    if resp_plate.choices:
        txt = resp_plate.choices[0].message.content.strip()
        alnum = ''.join(filter(str.isalnum, txt.splitlines()[0]))
        if 2 <= len(alnum) <= 10:
            plate = alnum

    # Step 2: extract state if plate found
    state = None
    if plate:
        resp_state = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You extract only the state name."},
                {"role": "user", "content": [
                    {"type": "text", "text": "Extract only the state name."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]}
            ],
            max_tokens=50
        )
        if resp_state.choices:
            state = resp_state.choices[0].message.content.strip().splitlines()[0]

    return plate, state, file_ts, data_ts

class WatcherHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory: return
        if not event.src_path.lower().endswith((".jpg", ".jpeg", ".png")): return
        plate, state, file_ts, data_ts = process_license_plate(event.src_path)
        new_name = f"{file_ts}.png" if plate else f"{file_ts}_NoPlate.png"
        dest = os.path.join(PROCESSED_FOLDER, new_name)
        shutil.move(event.src_path, dest)
        print(f"✅ Moved to {dest}")

def start_watch():
    print(f"👀 Watching {WATCH_FOLDER}")
    obs = Observer()
    obs.schedule(WatcherHandler(), WATCH_FOLDER, recursive=False)
    obs.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()

if __name__ == "__main__":
    start_watch()