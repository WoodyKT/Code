class dataControls:
    def WriteData(self):
      with open("static/sensorData.txt", "w") as w:
          import random
          output = ",".join(str(random.randint(0,1000)) for _ in range(5))
          print(output)
          w.write(output)
           