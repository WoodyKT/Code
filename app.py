from flask import Flask, render_template
from smartPotDisplay import *
from apscheduler.schedulers.background import BackgroundScheduler
import threading
import subprocess
import requests
import time
from PIL import Image
from inky.auto import auto
import os
import asyncio

# Flask setup
app = Flask(__name__)

# Screenshot and Flask settings
OUTPUT_PATH = "/home/woody/Code/screenshot.png"
LOCAL_URL = "http://127.0.0.1:5000"
LAN_URL = "http://192.168.137.126:5000"  # Optional LAN access
URL = None  # Will be chosen dynamically

# Flask route
@app.route("/")
def display():
    return render_template("display.html")

# Sensor file update job
def UpdateSensorFile():
    dataControl.WriteData()

schedule = BackgroundScheduler()
schedule.add_job(UpdateSensorFile, 'interval', seconds=5)

# Check Flask availability
def wait_for_flask(url, timeout=15):
    for _ in range(timeout):
        try:
            r = requests.get(url)
            if r.status_code == 200:
                print(f"[INFO] Flask is up at {url}")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    return False

# Screenshot using wkhtmltoimage
def take_screenshot(url, output_path, width=980, height=797):
    try:
        print("[DEBUG] Taking screenshot via wkhtmltoimage...")

        # Remove old screenshot if it exists
        if os.path.exists(output_path):
            os.remove(output_path)

        result = subprocess.run(
            [
                "wkhtmltoimage",
                "--width", str(width),
                "--height", str(height),
                url,
                output_path
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0 and os.path.exists(output_path):
            size = os.path.getsize(output_path)
            print(f"[DEBUG] Screenshot saved to {output_path} ({size} bytes)")
            # Sanity check: ignore tiny blank files
            if size < 10 * 1024:  # 10 KB
                print("[WARN] Screenshot too small, likely blank")
                return False
            return True
        else:
            print("[ERROR] wkhtmltoimage failed")
            print("[DEBUG] STDERR:", result.stderr.strip())
            return False

    except FileNotFoundError:
        print("[ERROR] wkhtmltoimage not installed. Run: sudo apt install wkhtmltopdf")
        return False
    except subprocess.TimeoutExpired:
        print("[ERROR] wkhtmltoimage timed out while taking screenshot")
        return False

# Update Inky display
def update_inky(image_path):
    try:
        print("[DEBUG] Updating Inky display...")
        inky_display = auto()
        img = Image.open(image_path).convert("RGB")
        img = img.resize(inky_display.resolution)
        inky_display.set_image(img)
        inky_display.show()
        print("[DEBUG] Inky display updated successfully")
    except FileNotFoundError:
        print(f"[ERROR] Screenshot not found at {image_path}")
    except Exception as e:
        print(f"[ERROR] Failed to update Inky display: {e}")

# Capture loop
async def capture_loop():
    while True:
        await asyncio.sleep(3)  # small delay before first capture

        success = take_screenshot(URL, OUTPUT_PATH)
        if success:
            update_inky(OUTPUT_PATH)
        else:
            print("[ERROR] No screenshot available, skipping Inky update")

        print("[DEBUG] Waiting 60 seconds until next capture")
        await asyncio.sleep(60)

if __name__ == "__main__":
    dataControl = dataControls()
    schedule.start()

    # Start Flask in background thread
    flask_thread = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False),
        daemon=True
    )
    flask_thread.start()

    # Small startup delay
    time.sleep(2)

    # Pick best URL
    if wait_for_flask(LOCAL_URL):
        URL = LOCAL_URL
    elif wait_for_flask(LAN_URL):
        URL = LAN_URL
    else:
        print("[ERROR] Flask not reachable")
        exit(1)

    print(f"[INFO] Using Flask URL: {URL}")

    # Run async capture loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(capture_loop())
    loop.run_forever()
