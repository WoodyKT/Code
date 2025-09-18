from flask import Flask, render_template
from smartPotDisplay import *
from apscheduler.schedulers.background import BackgroundScheduler
import threading
import asyncio
import requests
from pyppeteer import launch
from PIL import Image
from inky.auto import auto
import time

# Flask setup
app = Flask(__name__)
simulated = False

def UpdateSensorFile():
    dataControl.WriteData()

# Background job to update sensor file
schedule = BackgroundScheduler()
schedule.add_job(UpdateSensorFile, 'interval', seconds=5)

@app.route("/")
def display():
    return render_template("display.html")

# Screenshot + Inky update
PI_IP = "192.168.137.126"  # Your Pi's IP on network
URL = f"http://{PI_IP}:5000"
OUTPUT_PATH = "/home/woody/Code/screenshot.png"

def wait_for_flask(url, timeout=15):
    for _ in range(timeout):
        try:
            r = requests.get(url)
            if r.status_code == 200:
                print("Flask is up!")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    print("Flask server never became available")
    return False

async def take_screenshot():
    print("[DEBUG] Starting screenshot task...")

    # Wait until Flask server responds
    for i in range(10):
        try:
            r = requests.get(URL)
            if r.status_code == 200:
                print(f"[DEBUG] Flask responded, proceeding with screenshot (attempt {i+1})")
                break
        except requests.exceptions.RequestException:
            print(f"[DEBUG] Flask not reachable, retry {i+1}/10")
        await asyncio.sleep(1)
    else:
        print("[ERROR] Flask server not reachable after 10 attempts, skipping screenshot")
        return

    # Launch Chromium
    try:
        browser = await launch(
            headless=True,
            executablePath='/usr/bin/chromium',  # adjust if needed
            args=['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage']
        )
        print("[DEBUG] Chromium launched successfully")
    except Exception as e:
        print(f"[ERROR] Failed to launch Chromium: {e}")
        return

    # Open page and take screenshot
    try:
        page = await browser.newPage()
        await page.setViewport({'width': 980, 'height': 797})
        await page.goto(URL, waitUntil='networkidle2')
        await page.screenshot({'path': OUTPUT_PATH})
        await browser.close()
        print(f"[DEBUG] Screenshot saved to {OUTPUT_PATH}")
    except Exception as e:
        print(f"[ERROR] Failed to take screenshot: {e}")
        return

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

async def capture_loop():
    while True:
        await asyncio.sleep(3)  # small delay before first capture
        await take_screenshot()
        update_inky(OUTPUT_PATH)
        print("[DEBUG] Waiting 60 seconds until next capture")
        await asyncio.sleep(60)
if __name__ == "__main__":
    dataControl = dataControls()

    # Start the sensor update scheduler
    schedule.start()

    # Start Flask in a background thread so it doesn't block asyncio loop
    flask_thread = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False), daemon=True)
    flask_thread.start()
    if not wait_for_flask(URL):
        exit(1)

    # Run the async capture loop in the main thread event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(capture_loop())
    loop.run_forever()

