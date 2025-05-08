from flask import Flask, redirect,render_template
from smartPotDisplay import *

app = Flask(__name__)


@app.route("/")
def display(): 
    return render_template("display.html",weather  = getWeather(),        humidity    = getHumiditySensor(),
                                          moisture = getMoistureSensor(), waterLevel  = getWaterLevel(),
                                          light    = getLightSensor(),    temperature = getTemperatureSensor())


if __name__ == "__main__":
    app.run(debug=True)