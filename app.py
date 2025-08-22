from flask import Flask, render_template
from smartPotDisplay import *
from apscheduler.schedulers.background import BackgroundScheduler
import subprocess
import threading
import time
import asyncio
import requests
from pyppeteer import launch
from PIL import Image
from inky.auto import auto
import sys

# Flask setup
app = Flask(__name__)
simulated = False
displayOption = 1

def UpdateSensorFile():
    dataControl.WriteData(simulated)

# Background job to update sensor file
schedule = BackgroundScheduler()
schedule.add_job(UpdateSensorFile, 'interval', seconds=1)

@app.route("/")
def display():
    return render_template(f"display{displayOption}.html")

# Screenshot + Inky update
PI_IP = "192.168.137.134"  
URL = f"http://{PI_IP}:5000"
OUTPUT_PATH = "/home/woody/Code/screenshot.png"

# Buttons
BUTTONS = [5, 6, 16, 24] # 16 and 24 are the bottom 2
LABELS = ["A", "B", "C", "D"]
INPUT = gpiod.LineSettings(direction=Direction.INPUT, bias=Bias.PULL_UP, edge_detection=Edge.FALLING)
chip = gpiodevice.find_chip_by_platform()

# Build our config for each pin/line we want to use
OFFSETS = [chip.line_offset_from_id(id) for id in BUTTONS]
line_config = dict.fromkeys(OFFSETS, INPUT)

# Request the lines, *whew*
request = chip.request_lines(consumer="inky7-buttons", config=line_config)


# "handle_button" will be called every time a button is pressed
# It receives one argument: the associated gpiod event object.
def handle_button(event):
    index = OFFSETS.index(event.line_offset)
    gpio_number = BUTTONS[index]
    label = LABELS[index]
    if label == "C":
        displayOption=3-displayOption
    elif label == "D":
        print("debug")
    

async def take_screenshot():
    # Wait until server responds
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
    except:
        print("Error, likely no inky screen connected")

async def capture_loop():
    while True:
        await asyncio.sleep(3)
        await take_screenshot()
        update_inky(OUTPUT_PATH)
        await asyncio.sleep(5)

if __name__ == "__main__":
    if sys.argv[1] == "sim":
        simulated = True
    dataControl = dataControls(simulated)

    # Start the sensor update scheduler
    schedule.start()

    # Start Flask in a background thread so it doesn't block asyncio loop
    flask_thread = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False), daemon=True)
    flask_thread.start()

    # Run the async capture loop in the main thread event loop
    asyncio.run(capture_loop())
    
while True:
    for event in request.read_edge_events():
        handle_button(event)
