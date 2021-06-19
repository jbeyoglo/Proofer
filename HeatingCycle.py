from datetime import datetime, timedelta

class HeatingCycle:
	startDateTime: datetime = datetime.now()
	secondsHeaterOn: int 
	deltaTimeMS: int = 0
	deltaTempC: float = 0.0

	__startingTemp: float
	__trackTemp: float 
	__minReductionTrack: float = 0.05


	def __init__(self, duration = 10):
		self.secondsHeaterOn = duration

	def restart(self, currentTemp):
		self.startDateTime = datetime.now()
		self.__startingTemp = currentTemp

	def isTimeToStart(self, currentTemp, targetTemp):
		return ( (currentTemp + self.deltaTempC) < targetTemp )

	def shouldStartNow(self, currentTemp, targetTemp):
		# if is the right moment start the new cycle
		if (currentTemp + self.deltaTempC) < targetTemp:
			self.restart(currentTemp) 
			return True
		# if not.. do nothing, ..wait.
		return False

	def stopHeaterTime(self):
		return self.startDateTime + timedelta(seconds=self.secondsHeaterOn)

	def shouldStopNow(self, currentTemp):
		#if( datetime.now() > self.stopHeaterTime ):
		if( datetime.now() > (self.startDateTime + timedelta(seconds=self.secondsHeaterOn)) ): 
			self.__trackTemp = currentTemp
			return True
		return False

	def isFinished(self, currentTemp):
		# temp grew or didn't fall enough 
		if( (currentTemp + self.__minReductionTrack) >= self.__trackTemp ):
			# keep track if the temperature really grew
			if( currentTemp > self.__trackTemp ):
				self.__trackTemp = currentTemp
			return False;
		# cycle is over => keep track of the deltas
		self.deltaTempC = currentTemp - self.__startingTemp
		#deltaTimeMS = ...later
		return True;
