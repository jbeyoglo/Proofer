#!/usr/bin/python3

import io
from picamera import PiCamera
from time import sleep
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import sys


stream = io.BytesIO()
with PiCamera() as camera:
	camera.resolution = (1280, 720)
	camera.start_preview()
	sleep(2)
	camera.capture(stream, format='jpeg')

# "Rewind" the stream to the beginning so we can read its content
stream.seek(0)
image = Image.open(stream)

fontsize = 100  # starting font size
font = ImageFont.truetype("arialr.ttf", fontsize)
draw = ImageDraw.Draw(image)

# time
draw.text((880, 100), datetime.today().strftime('%H:%M'), font=font, fill='white', stroke_width=2)

# time elapsed
if( len(sys.argv) >= 1 ):
	draw.text((880, 220), sys.argv[1], font=font, fill='white', stroke_width=2)

if( len(sys.argv) >= 2 ):
	draw.text((880, 450), sys.argv[2], font=font, fill='yellow', stroke_width=2)

image.show()
image.save('image.jpg')
