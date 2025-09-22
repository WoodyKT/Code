from flask import Flask, render_template
from smartPotDisplay import *
from apscheduler.schedulers.background import BackgroundScheduler
import threading
import asyncio
import requests
from pyppeteer import launch
from PIL import Image
from inky.auto import auto
import os
import time

# Flask setup
app = Flask(__name__)

# Screenshot settings
OUTPUT_PATH = "/home/woody/Code/screenshot.png"
LOCAL_URL = "http://127.0.0.1:5000"
LAN_URL = "http://192.168.137.126:5000"
URL = None

# Flask route
@app.route("/")
def display():
    return render_template("display.html")

# Sensor file update job
def UpdateSensorFile():
    dataControl.WriteData()

schedule = BackgroundScheduler()
schedule.add_job(UpdateSensorFile, 'interval', seconds=5)

# Wait for Flask server to start
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

# Take screenshot with pyppeteer
async def take_screenshot_pyppeteer(url, output_path, width=980, height=797):
    try:
        print("[DEBUG] Launching Chromium via pyppeteer...")
        browser = await launch(headless=True,
                               args=['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage'])
        page = await browser.newPage()
        await page.setViewport({'width': width, 'height': height})
        await page.goto(url, waitUntil='networkidle2')  # wait for JS to finish

        # Wait for elements we know must be loaded
        await page.waitForSelector('.time', timeout=10000)
        await page.waitForSelector('.weatherIcon', timeout=10000)

        # Take screenshot
        await page.screenshot({'path': output_path})
        await browser.close()
        print(f"[DEBUG] Screenshot saved to {output_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to take screenshot: {e}")
        return False

# Async capture loop
async def capture_loop():
    while True:
        await asyncio.sleep(3)  # initial delay
        success = await take_screenshot_pyppeteer(URL, OUTPUT_PATH)
        if success:
            update_inky(OUTPUT_PATH)
        else:
            print("[ERROR] Screenshot failed, skipping Inky update")
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

    time.sleep(2)

    # Pick working URL
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
