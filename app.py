from flask import Flask, redirect,render_template
from smartPotDisplay import *
from selenium import webdriver
import time

app = Flask(__name__)

@app.route("/")
def display():
    weather, timeColour = getWeather()
    humidity, humidityValue = getHumiditySensor()
    moisture, moistureValue = getMoistureSensor()
    water,waterValue = getWaterLevel()
    light, lightValue = getLightSensor()
    temperature, temperatureValue = getTemperatureSensor()

    return render_template("display.html",weather = weather,        humidity    = humidity,
                                          moisture = moisture, water  = water,
                                          light    = light,    temperature = temperature,
                                          time = getTime(), timeColour = 'style = color:' + timeColour,
                                          
                                          humidityValue = humidityValue, moistureValue = moistureValue, 
                                          waterValue = waterValue, lightValue = lightValue, temperatureValue = temperatureValue)


if __name__ == "__main__":
    app.run(debug=True)
