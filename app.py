from flask import Flask, redirect,render_template
from smartPotDisplay import *
from selenium import webdriver
import time

app = Flask(__name__)


@app.route("/")
def display():
    weather, timeColour = getWeather()
    return render_template("display.html",weather = weather,        humidity    = getHumiditySensor(),
                                          moisture = getMoistureSensor(), waterLevel  = getWaterLevel(),
                                          light    = getLightSensor(),    temperature = getTemperatureSensor(),
                                          time = getTime(), timeColour = 'style = color:' + timeColour)


if __name__ == "__main__":
    app.run(debug=True)
