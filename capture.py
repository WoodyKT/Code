import asyncio
import time
import requests
from pyppeteer import launch
from PIL import Image
from inky.auto import auto

PI_IP = "192.168.137.134"
OUTPUT_PATH = "/home/woody/Code/screenshot.png"
URL = f"http://{PI_IP}:5000"

async def TakeScreenshot():
    # Wait until server responds
    for _ in range(10):
        try:
            r = requests.get(URL)
            if r.status_code == 200:
                break
        except requests.exceptions.RequestException:
            time.sleep(1)
    else:
        print("Server not reachable")
        return

    browser = await launch(
        headless=True,
        executablePath='/usr/bin/chromium-browser',
        args=['--no-sandbox']
    )
    page = await browser.newPage()
    await page.setViewport({'width': 980, 'height': 797})
    await page.goto(URL, waitUntil='networkidle2')
    await page.screenshot({'path': OUTPUT_PATH})
    await browser.close()

    print(f"Saved screenshot to {OUTPUT_PATH}")

def DisplayOnInky(image_path):
    print("Displaying image on Inky Impression...")
    inky_display = auto()
    img = Image.open(image_path).convert("RGB")

    # Resize to match the Inky Impression resolution
    img = img.resize(inky_display.resolution)

    inky_display.set_image(img)
    inky_display.show()
    print("Image displayed.")

# Main run
asyncio.run(TakeScreenshot())
DisplayOnInky(OUTPUT_PATH)
