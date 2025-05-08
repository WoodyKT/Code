import random



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
    return weather[random.randint(0,7)]




def getWeather():

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