import random
from apscheduler.schedulers.background import BackgroundScheduler


class dataControls:
    _data = ["light","humidity","moisture","temperature","waterLevel"]

    #Write data in csv format to file
    def WriteData(self, simulated):
        with open("static/sensorData.txt","w") as w:
            if simulated:
                output =""
                for i in self._data:
                    output=output+(str(random.randint(0,1000))+",")
            w.write(output[0:len(output)-1])
        # else:
               #read sensor code