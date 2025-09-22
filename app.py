from flask import Flask, render_template
from smartPotDisplay import *
from apscheduler.schedulers.background import BackgroundScheduler
import threading
import requests
import time
import subprocess
from PIL import Image
from inky.auto import auto
import os
import asyncio
import RPi.GPIO as GPIO
import os
import time
import threading

BUTTON_A = 5  # BCM pin for Button A

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def shutdown_listener():
    print("Waiting for Inky Button A press to shutdown...")
    try:
        while True:
            if GPIO.input(BUTTON_A) == 0:  # Button pressed
                print("Button A pressed! Shutting down...")
                os.system("sudo shutdown now")
                break
            time.sleep(0.1)  # debounce
    finally:
        GPIO.cleanup()

# Run listener in a background thread
threading.Thread(target=shutdown_listener, daemon=True).start()

# ------------------------
# Flask setup
# ------------------------
app = Flask(__name__)
weather_icon = "sunny"
# Inky Impression resolution
INKY_WIDTH = 600
INKY_HEIGHT = 448

# Original viewport size you designed for in Chromium
VIEWPORT_WIDTH = 980
VIEWPORT_HEIGHT = 797
OUTPUT_PATH = "/home/woody/Code/screenshot.png"
URL = "http://127.0.0.1:5000"

# ------------------------
# Sensor + Weather
# ------------------------
dataControl = dataControls()

schedule = BackgroundScheduler()
schedule.add_job(dataControl.WriteData, 'interval', seconds=5)
schedule.start()


def get_weather_icon():
    try:
        apiKey = "99d05d20435a20010a1a2f22deb59bc0"
        city = "Coventry"
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={apiKey}"
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        data = res.json()
        weather_main = data['weather'][0]['main']
        weather_map = {
            "Clear": "sunny",
            "Clouds": "sunnyCloud",
            "Rain": "rainy",
            "Drizzle": "sunnyRain",
            "Thunderstorm": "stormy",
            "Snow": "snowy",
            "Mist": "foggy",
            "Smoke": "foggy",
            "Haze": "foggy",
            "Dust": "foggy",
            "Fog": "foggy",
            "Sand": "foggy",
            "Ash": "foggy",
            "Squall": "stormy",
            "Tornado": "stormy"
        }
        return weather_map.get(weather_main, "sunny")
    except Exception as e:
        print(f"[WARN] Failed to fetch weather: {e}")
        return "sunny"


def get_color(value):
    try:
        value = int(value)
        if value < 25:
            return "red"
        elif value < 200:
            return "orange"
        else:
            return "green"
    except:
        return "green"

# ------------------------
# Flask route (server-side rendering)
# ------------------------
@app.route("/")
def display():
    # Read sensor data
    try:
        with open("static/sensorData.txt") as f:
            values = f.read().strip().split(',')
            light = values[0] if len(values) > 0 else "0"
            humidity = values[1] if len(values) > 1 else "0"
            moisture = values[2] if len(values) > 2 else "0"
            temperature = values[3] if len(values) > 3 else "0"
            water = values[4] if len(values) > 4 else "0"
    except Exception as e:
        print(f"[WARN] Failed to read sensor file: {e}")
        light = humidity = moisture = temperature = water = "0"

    weather_icon = get_weather_icon()

    return render_template(
        "display.html",
        time_str=time.strftime("%H:%M"),
        light=light,
        humidity=humidity,
        moisture=moisture,
        temperature=temperature,
        water=water,
        light_icon=get_color(light),
        humidity_icon=get_color(humidity),
        moisture_icon=get_color(moisture),
        temperature_icon=get_color(temperature),
        water_icon=get_color(water),
        weather_icon=weather_icon
    )

# ------------------------
# Screenshot + Inky update
# ------------------------
WKHTML_WIDTH = 600
WKHTML_HEIGHT = 448

def take_screenshot(url=URL, output_path=OUTPUT_PATH):
    """
    Take a screenshot of the Flask-rendered page using wkhtmltoimage,
    keeping original CSS layout and scaling to Inky display.
    """
    try:
        # Remove previous screenshot
        if os.path.exists(output_path):
            os.remove(output_path)

        # Calculate zoom factor to scale viewport to Inky resolution
        zoom_width = INKY_WIDTH / VIEWPORT_WIDTH
        zoom_height = INKY_HEIGHT / VIEWPORT_HEIGHT
        zoom = min(zoom_width, zoom_height)  # maintain aspect ratio

        # Run wkhtmltoimage
        subprocess.run([
            "wkhtmltoimage",
            "--width", str(VIEWPORT_WIDTH),
            "--height", str(VIEWPORT_HEIGHT),
            "--zoom", str(zoom),
            url,
            output_path
        ], check=True, timeout=30)

        print(f"[INFO] Screenshot taken and scaled to {INKY_WIDTH}x{INKY_HEIGHT}")
        return True

    except Exception as e:
        print(f"[ERROR] Screenshot failed: {e}")
        return False



def update_inky(image_path=OUTPUT_PATH):
    try:
        inky_display = auto()
        img = Image.open(image_path).convert("RGB")
        img = img.resize(inky_display.resolution)
        inky_display.set_image(img)
        inky_display.show()
        print("[INFO] Inky display updated")
    except Exception as e:
        print(f"[ERROR] Inky update failed: {e}")

# ------------------------
# Async capture loop
# ------------------------
async def capture_loop():
    while True:
        await asyncio.sleep(3)  # small initial delay
        if take_screenshot():
            update_inky()
        else:
            print("[ERROR] Screenshot failed, skipping Inky update")
        await asyncio.sleep(60)  # repeat every 60s

# ------------------------
# Main
# ------------------------
if __name__ == "__main__":
    # Start Flask in background
    flask_thread = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False),
        daemon=True
    )
    flask_thread.start()

    # Small delay for Flask to start
    time.sleep(2)

   # Wait up to 20 seconds for Flask
    for i in range(20):
        try:
            r = requests.get(URL, timeout=3)
            if r.status_code == 200:
                print("[INFO] Flask server is ready")
                break
        except requests.exceptions.RequestException:
            print(f"[DEBUG] Waiting for Flask... ({i+1}/20)")
        time.sleep(1)
    else:
        print("[ERROR] Flask did not start")
        exit(1)


    # Start asyncio capture loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(capture_loop())
    loop.run_forever()
