class dataControls:
    def WriteData(self):
      with open("static/sensorData.txt", "w") as w:
          import random
          output = ",".join(str(random.randint(0,1000)) for _ in self._data)
          print(output)
          w.write(output)
           