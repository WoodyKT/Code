from flask import Flask, render_template
from smartPotDisplay import *
from apscheduler.schedulers.background import BackgroundScheduler
import threading
import subprocess
import requests
import time
from PIL import Image
from inky.auto import auto

# Flask setup
app = Flask(__name__)

# Global vars
OUTPUT_PATH = "screenshot.png"
LOCAL_URL = "http://127.0.0.1:5000"
LAN_URL = "http://192.168.137.126:5000"  # your Pi's LAN IP
URL = None  # chosen dynamically

# Flask route
@app.route("/")
def display():
    return render_template("display.html")

# Sensor update job
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

# Screenshot via Chromium CLI
def take_screenshot_cli(url, output_path, width=980, height=797):
    try:
        print("[DEBUG] Taking screenshot via Chromium CLI...")
        result = subprocess.run(
            [
                "chromium-browser",  # or "chromium" depending on your system
                "--headless",
                "--disable-gpu",
                f"--screenshot={output_path}",
                f"--window-size={width},{height}",
                url,
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print(f"[DEBUG] Screenshot saved to {output_path}")
        else:
            print("[ERROR] Chromium CLI failed:")
            print(result.stderr)
    except FileNotFoundError:
        print("[ERROR] chromium-browser not found. Install with: sudo apt install chromium-browser")
    except subprocess.TimeoutExpired:
        print("[ERROR] Chromium CLI timed out while taking screenshot")

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
def capture_loop():
    while True:
        time.sleep(3)
        take_screenshot_cli(URL, OUTPUT_PATH)
        update_inky(OUTPUT_PATH)
        print("[DEBUG] Waiting 60 seconds until next capture")
        time.sleep(60)

if __name__ == "__main__":
    dataControl = dataControls()
    schedule.start()

    # Start Flask in background thread
    flask_thread = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False),
        daemon=True
    )
    flask_thread.start()

    # Small boot delay
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

    # Run main loop
    capture_loop()
