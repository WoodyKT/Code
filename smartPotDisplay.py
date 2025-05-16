import random, python_weather
from datetime import datetime




def simulateSensorData():
    data = random.randint(1,1000)
    
    if data<100 or data>900:
        return "red",data
    elif data <250 or data>750:
        return "orange",data
    else:
        return "green",data
    
def simulateWeatherData():
    weather = ["cloudy",  "sunnyCloud","foggy",   "rainy","snowy",    "stormy","sunny", "sunnyRain"]
    colours = ["darkBlue","orange",    "darkBlue","white","darkBlue","white", "orange","white"]
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
    indicator, value = simulateSensorData()    
    return indicator, value

def getMoistureSensor():
    indicator, value = simulateSensorData()
    return indicator, value

def getHumiditySensor():
    indicator, value = simulateSensorData()
    return indicator, value

def getWaterLevel():
    indicator, value = simulateSensorData()
    return indicator, value

def getTemperatureSensor():
    indicator, value = simulateSensorData()
    return indicator, value

def getTime(): return datetime.now().strftime("%H:%M")


    
    




    