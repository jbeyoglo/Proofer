from datetime import datetime, timedelta

class HeatingCycle:
    startDateTime: datetime = datetime.now()
    secondsHeaterOn: int = 10
    deltaTimeMS: int = 0
    deltaTempC: float = 0.0

    def __init__(duration):
        self.secondsHeaterOn = duration

	def restart(self):
        self.startDateTime = datetime.now()
	
	def isTimeToStart(self, currentTemp, targetTemp):
		return ( (currentTemp + deltaTempC) < targetTemp )

	def shouldStartNow(self, currentTemp, targetTemp):
		# if is the right moment start the new cycle
		if (currentTemp + deltaTempC) < targetTemp:
			self.restart() 
			return true
		# if not.. do nothing, ..wait.
		return false

	def stopHeaterTime(self):
		return self.startDateTime + timedelta(seconds=self.secondsHeaterOn)

	def shouldStopNow(self, currentTemp):
		if( datetime.now() > self.stopHeaterTime ):
			return true
		return false

