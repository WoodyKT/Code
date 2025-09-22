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

OUTPUT_PATH = "/home/woody/Code/screenshot.png"
LOCAL_URL = "http://127.0.0.1:5000"
LAN_URL = "http://192.168.137.126:5000"
URL = None

@app.route("/")
def display():
    return render_template("display.html")

# Sensor update job
def UpdateSensorFile():
    dataControl.WriteData()

schedule = BackgroundScheduler()
schedule.add_job(UpdateSensorFile, 'interval', seconds=5)

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

def update_inky(image_path):
    try:
        inky_display = auto()
        img = Image.open(image_path).convert("RGB")
        img = img.resize(inky_display.resolution)
        inky_display.set_image(img)
        inky_display.show()
        print("[DEBUG] Inky updated")
    except Exception as e:
        print(f"[ERROR] Failed to update Inky: {e}")

class Screenshotter:
    def __init__(self, url, output_path, width=980, height=797):
        self.url = url
        self.output_path = output_path
        self.width = width
        self.height = height
        self.browser = None
        self.page = None

    async def launch_browser(self):
        print("[DEBUG] Launching Chromium")
        self.browser = await launch(
    executablePath='/usr/bin/chromium-browser',  # or '/usr/bin/chromium'
    headless=True,
    args=['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage']
)
        self.page = await self.browser.newPage()
        await self.page.setViewport({'width': self.width, 'height': self.height})
        await self.page.goto(self.url, waitUntil='networkidle2')
        print("[DEBUG] Browser ready")

    async def refresh_content_and_screenshot(self):
        try:
            # Trigger JS functions in the page to update data
            await self.page.evaluate('Update(); UpdateWeather();')

            # Wait for key elements to exist
            await self.page.waitForSelector('.time', timeout=5000)
            await self.page.waitForSelector('.weatherIcon', timeout=5000)

            # Take screenshot
            await self.page.screenshot({'path': self.output_path})
            size = os.path.getsize(self.output_path)
            if size < 10*1024:
                print("[WARN] Screenshot too small, likely blank")
                return False
            print("[DEBUG] Screenshot saved")
            return True
        except Exception as e:
            print(f"[ERROR] Screenshot failed: {e}")
            return False

    async def close_browser(self):
        if self.browser:
            await self.browser.close()
            print("[DEBUG] Browser closed")

async def capture_loop(screenshotter):
    while True:
        await asyncio.sleep(3)  # initial delay
        success = await screenshotter.refresh_content_and_screenshot()
        if success:
            update_inky(OUTPUT_PATH)
        else:
            print("[ERROR] Failed screenshot, skipping Inky update")
        await asyncio.sleep(60)

if __name__ == "__main__":
    dataControl = dataControls()
    schedule.start()

    flask_thread = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False),
        daemon=True
    )
    flask_thread.start()
    time.sleep(2)

    if wait_for_flask(LOCAL_URL):
        URL = LOCAL_URL
    elif wait_for_flask(LAN_URL):
        URL = LAN_URL
    else:
        print("[ERROR] Flask not reachable")
        exit(1)
    print(f"[INFO] Using URL: {URL}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    screenshotter = Screenshotter(URL, OUTPUT_PATH)
    loop.run_until_complete(screenshotter.launch_browser())
    loop.create_task(capture_loop(screenshotter))
    loop.run_forever()
