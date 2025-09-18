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
    # Wait until server responds
    print("attempting screenshot")
    for _ in range(10):
        try:
            r = requests.get(URL)
            if r.status_code == 200:
                break
        except requests.exceptions.RequestException:
            await asyncio.sleep(1)
    else:
        print("Server not reachable")
        return

    browser = await launch(
    headless=True,
    executablePath='/usr/bin/chromium-browser',
    args=[
        '--no-sandbox',
        '--disable-gpu',
        '--disable-dev-shm-usage'
    ]
)
    print("waiting for page")
    page = await browser.newPage()
    await page.setViewport({'width': 980, 'height': 797})
    await page.goto(URL, waitUntil='networkidle2')
    await page.screenshot({'path': OUTPUT_PATH})
    await browser.close()
    print(f"Saved screenshot to {OUTPUT_PATH}")

def update_inky(image_path):
    print("Updating Inky Impression display...")
    try:
        inky_display = auto()
        img = Image.open(image_path).convert("RGB")
        img = img.resize(inky_display.resolution)
        inky_display.set_image(img)
        inky_display.show()
        print("Inky display updated.")
    except Exception as e:
        print(f"Error updating Inky display: {e}")

async def capture_loop():
    while True:
        await asyncio.sleep(3)
        await take_screenshot()
        update_inky(OUTPUT_PATH)
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

