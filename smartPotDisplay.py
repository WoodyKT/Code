from gpiozero import MCP3008
import RPi.GPIO
import time

class dataControls:
    _data = ["light", "humidity", "moisture", "temperature", "waterLevel"]

    def __init__(self):
        # Map each sensor to a MCP3008 channel
        # Channels: 0..7
        self.light      = MCP3008(channel=0)  # Light sensor
        self.humidity   = MCP3008(channel=1)  # Humidity sensor
        self.moisture   = MCP3008(channel=2)  # Soil moisture sensor
        self.temperature= MCP3008(channel=3)  # Temperature sensor
        self.waterLevel = MCP3008(channel=4)  # Water level sensor
        self.pumpPin = 26

    def ActivatePump(self, pumpTime):
        RPi.GPIO.output(self.pumpPin,RPi.GPIO.HIGH)
        time.sleep(pumpTime)
        RPi.GPIO.output(self.pumpPin,RPi.GPIO.LOW)


    def WriteData(self, simulated=True):
        with open("static/sensorData.txt", "w") as w:
            if simulated:
                # Generate fake values for testing
                import random
                output = ",".join(str(random.randint(0, 1000)) for _ in self._data)
            else:
                # Read real ADC values (0.0 to 1.0 → scale to 0–1000)
                output = ",".join(str(int(sensor.value * 1000)) for sensor in [
                    self.light,
                    self.humidity,
                    self.moisture,
                    self.temperature,
                    self.waterLevel
                ])
            w.write(output)
            pumpTime = 0
            if self.humidity.sensor.value <0.4:
                print("Low humidity, activating pump")
                pumpTime+=2
            elif self.moisture.sensor.value <0.3:
                print("Low moisture, activating pump")
                pumpTime+=4
            if not pumpTime==0:
                self.ActivatePump(pumpTime)