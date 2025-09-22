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
OUTPUT_PATH = "/home/woody/Code/screenshot.png"
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
            t
