from flask import Flask,render_template
from smartPotDisplay import *

app = Flask(__name__)
simulated = True
def UpdateSensorFile():
    dataControl.WriteData(simulated)

#Update sensor data file in background
schedule = BackgroundScheduler()
schedule.add_job(UpdateSensorFile,'interval',seconds=1)
schedule.start()

#Display screen
@app.route("/")
def display():
    return render_template("display.html")

if __name__ == "__main__":
    dataControl = dataControls()
    app.run(debug=False,use_reloader=False)
   # subprocess.run(["python", "capture.py"])

