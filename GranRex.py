#!/usr/bin/python3

import time
from datetime import datetime, timedelta
from enum import Enum
import logging, sys
from HeatingCycle import HeatingCycle
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# Led Display - 4 digitsn I2C
import tm1637

# Temperature sensor
from htu21 import HTU21 


# GPIO
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
PIN_FAN = 23
PIN_HEATER = 24
GPIO.setwarnings(False)
GPIO.setup(PIN_FAN, GPIO.OUT)
GPIO.setup(PIN_HEATER, GPIO.OUT)

PIN_SWITCH = 25
GPIO.setup(PIN_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def my_callback(PIN_SWITCH):
	print('***********************************')
	print('BOTONAZOOOO')
	print('***********************************')

GPIO.add_event_detect(PIN_SWITCH, GPIO.RISING, callback=my_callback, bouncetime=400)


class State(Enum):
	OFF = 0
	IDLE = 1
	HEATING = 2
	INERTIA = 3


led4dig  = tm1637.TM1637(clk=6, dio=5)
sensor = HTU21()

targetTemp = 27
currentState = State.IDLE
cycle = HeatingCycle()

heaterStartedAt = None

logging.info('Proofer starting at ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# loop forever
while True:

	currentTemp = sensor.read_temperature()
	intPart = int(currentTemp)
	decPart = int((currentTemp-intPart) * 100)
	led4dig.numbers( intPart, decPart )

	logging.debug('Current temp %6.2f', currentTemp)
	logging.debug('State: ' + currentState.name)

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
		if( cycle.isFinished(currentTemp) ):
			currentState = State.IDLE


	logging.debug('Final state: ' + currentState.name)
	logging.debug('========================')
	time.sleep(0.5)


