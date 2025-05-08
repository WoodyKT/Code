import random, python_weather
from datetime import datetime



def simulateSensorData():
    data = random.randint(1,1000)
    
    if data<100 or data>900:
        return "red"
    elif data <250 or data>750:
        return "orange"
    else:
        return "green"
    
def simulateWeatherData():
    weather = ["cloudy","sunnyCloud","foggy","rainy","snowy","stormy","sunny","sunnyRain"]
    colours = ["darkBlue","white","white","white","white","white","orange","white"]
    choice = random.randint(0,7)
    return weather[choice],colours[choice]

#def getWeatherAPI() -> None:
#    with python_weather.client(unit = python_weather.METRIC) as client:
#        weather =  client.get("London")
#        print(weather.forecast.kind)



def getWeather():
#    getWeatherAPI()
    return simulateWeatherData()



def getLightSensor():
    indicator = simulateSensorData()    
    return indicator

def getMoistureSensor():
    indicator = simulateSensorData()
    return indicator

def getHumiditySensor():
    indicator = simulateSensorData()
    return indicator

def getWaterLevel():
    indicator = simulateSensorData()
    return indicator

def getTemperatureSensor():
    indicator = simulateSensorData()
    return indicator

def getTime(): return datetime.now().strftime("%H:%M")


    