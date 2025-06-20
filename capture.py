import asyncio
import time
import requests
from pyppeteer import launch

async def TakeScreenshot():
    # Wait until server responds
    url = 'http://localhost:5000'
    for _ in range(10):
        try:
            requests.get(url)
            break
        except:
            time.sleep(1)
    else:
        print("Server not reachable")
        return

    browser = await launch(
        headless=True,
        executablePath='C:/Program Files/Google/Chrome/Application/chrome.exe',
        args=['--no-sandbox']
    )
    page = await browser.newPage()
    await page.setViewport({'width': 980, 'height': 797})
    await page.goto(url, waitUntil='networkidle2')
    await page.screenshot({'path': 'screenshot.png'})
    await browser.close()

asyncio.run(TakeScreenshot())
print("Saved")
