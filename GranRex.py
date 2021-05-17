#!/usr/bin/python3
import time
from enum import Enum
from HeatingCycle import HeatingCycle


# Led Display - 4 digitsn I2C
import tm1637

# Temperature sensor
from htu21 import HTU21 

# GPIO
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
PIN_FAN = 23
PIN_HEATER = 24
GPIO.setup(PIN_FAN, GPIO.OUT)
GPIO.setup(PIN_HEATER, GPIO.OUT)


class State(Enum):
	OFF = auto()
	IDLE = auto()
	HEATING = auto()
	INERTIA = auto()


led4dig  = tm1637.TM1637(clk=6, dio=5)
sensor = HTU21()

targetTemp = 17
currentState = State.IDLE
currentDateTime = datetime.datetime.now()
cycle = HeatingCycle()

heaterStartedAt = None

# loop forever
while True:

	currentTemp = sensor.temperature
	intPart = int(currentTemp)
	decPart = int((currentTemp-intPart) * 100)
	print( intPart , decPart)
	led4dig.numbers( intPart, decPart )


	if currentState == State.OFF:
		#make sure the heater and fan are off
		GPIO.output(PIN_FAN, GPIO.HIGH)
		GPIO.output(PIN_HEATER, GPIO.HIGH)

	elif currentState == State.IDLE:
		# time to start the heater?, if so then move to heating
		if( cycle.shouldStartNow(currentTemp, targetTemp) ):
			GPIO.output(PIN_HEATER, GPIO.LOW)
			GPIO.output(PIN_FAN, GPIO.LOW)
			currentState = State.HEATING

	elif currentState == State.HEATING:
		# wait the cicleTime and move to inertia
		if( cycle.shouldStopNow(currentTemp) ):
			GPIO.output(PIN_HEATER, GPIO.HIGH)
			currentState = State.INERTIA

	elif currentState == State.INERTIA:
		


	#if heaterStartedAt is None && currentTemp < targetTemp:


	
	time.sleep(0.1)

