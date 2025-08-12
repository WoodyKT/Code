from flask import Flask, render_template
from smartPotDisplay import *
from apscheduler.schedulers.background import BackgroundScheduler
import subprocess
import threading
import time

app = Flask(__name__)
simulated = True

def UpdateSensorFile():
    dataControl.WriteData(simulated)

# Update sensor data file in background
schedule = BackgroundScheduler()
schedule.add_job(UpdateSensorFile, 'interval', seconds=1)
schedule.start()

# Display screen
@app.route("/")
def display():
    return render_template("display.html")

def run_capture_after_delay():
    # Small delay to let Flask fully start
    time.sleep(3)
    subprocess.run(["python3", "capture.py"])

if __name__ == "__main__":
    dataControl = dataControls()

    # Start capture script in a background thread
    threading.Thread(target=run_capture_after_delay, daemon=True).start()

    # Run Flask accessible to other devices
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
