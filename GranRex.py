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
PIN_SWITCH = 12	# switch on/off
GPIO.setup(PIN_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)
TEMP_UP_SWITCH = 13
GPIO.setup(TEMP_UP_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)
TEMP_DOWN_SWITCH = 19
GPIO.setup(TEMP_DOWN_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# share variables with the configuration thread
import atomos.atomic
import Configuration as cfg
onOffSwitch = atomos.atomic.AtomicInteger( GPIO.input(PIN_SWITCH) == GPIO.LOW )
targetTemp = atomos.atomic.AtomicInteger( cfg.proofer["initialTargetTemperature"] )
timeLastSetup = atomos.atomic.AtomicInteger(0)

def my_callback(PIN_SWITCH):
	onOffSwitch.set( GPIO.input(PIN_SWITCH) == GPIO.LOW )

def tempUp_callback(TEMP_UP_SWITCH):
	targetTemp.add_and_get(1)
	timeLastSetup.set( int(datetime.now().timestamp()) )

def tempDown_callback(TEMP_DOWN_SWITCH):
	targetTemp.get_and_subtract(1)
	timeLastSetup.set( int(datetime.now().timestamp()) )

GPIO.add_event_detect(PIN_SWITCH, GPIO.BOTH, callback=my_callback, bouncetime=240)
GPIO.add_event_detect(TEMP_UP_SWITCH, GPIO.RISING, callback=tempUp_callback, bouncetime=180)
GPIO.add_event_detect(TEMP_DOWN_SWITCH, GPIO.RISING, callback=tempDown_callback, bouncetime=180)



class State(Enum):
	OFF = 0
	IDLE = 1
	HEATING = 2
	INERTIA = 3


led4dig  = tm1637.TM1637(clk=6, dio=5)
sensor = HTU21()

currentState = State.IDLE
cycle = HeatingCycle()

heaterStartedAt = None

logging.info('Proofer starting at ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# loop forever
while True:
	currentTemp = sensor.read_temperature()

	if( datetime.now().timestamp() > timeLastSetup.get() + 3 ):
		if( onOffSwitch.get() ):
			intPart = int(currentTemp)
			decPart = int((currentTemp-intPart) * 100)
			led4dig.numbers( intPart, decPart )
			# resume operation?
			if currentState == State.OFF:
				currentState = State.IDLE
		else: 
			led4dig.show(' Off')
			currentState = State.OFF
	else:
		led4dig.temperature( targetTemp.get() )



	logging.debug('%d // Current temp %6.2f // target %d', onOffSwitch.get(), currentTemp, targetTemp.get())
	logging.debug('State: ' + currentState.name)

	if currentState == State.OFF:
		#make sure the heater and fan are off
		GPIO.output(PIN_FAN, GPIO.HIGH)
		GPIO.output(PIN_HEATER, GPIO.HIGH)

	elif currentState == State.IDLE:
		# time to start the heater?, if so then move to heating
		if( cycle.shouldStartNow(currentTemp, targetTemp.get()) ):
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


