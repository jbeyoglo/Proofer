#!/usr/bin/python3

import time

# Led Display - 4 digitsn I2C
import tm1637

# Temperature sensor
import board
import busio
from adafruit_htu21d import HTU21D

# Create library object using our Bus I2C port
i2c = busio.I2C(board.SCL, board.SDA)
sensor = HTU21D(i2c)

led4dig  = tm1637.TM1637(clk=6, dio=5)




# loop forever
while True:

	currentTemp = sensor.temperature
	intPart = int(currentTemp)
	decPart = int((currentTemp-intPart) * 100)
	print( intPart , decPart)
	led4dig.numbers( intPart, decPart )

	if 
	

	time.sleep(2)

