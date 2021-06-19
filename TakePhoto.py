#!/usr/bin/python3

import io
from picamera import PiCamera
from time import sleep
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import sys
from pathlib import Path

import Configuration as cfg
resX = cfg.camera["resX"]
resY = cfg.camera["resY"]

Path( cfg.camera["path"] ).mkdir(parents=True, exist_ok=True)
imageName = cfg.camera["path"] + "/" + datetime.today().strftime("IMG_%y%m%d_%H%M%S.jpg")


stream = io.BytesIO()
with PiCamera() as camera:
	camera.resolution = (resX, resY)
	camera.start_preview()
	sleep( int(cfg.camera["secondsToFocus"]) )
	camera.capture(stream, format='jpeg')

# "Rewind" the stream to the beginning so we can read its content
stream.seek(0)
image = Image.open(stream)

fontsize = int(resX/15)  # starting font size
font = ImageFont.truetype("arialr.ttf", fontsize)
draw = ImageDraw.Draw(image)

# time
draw.text((int(resX/4*3), int(resY/13*2)), datetime.today().strftime('%H:%M'), font=font, fill='white', stroke_width=2)
# time elapsed
if( len(sys.argv) >= 1 ):
	draw.text((int(resX/4*3), int(resY/13*4)), sys.argv[1], font=font, fill='white', stroke_width=2)
# temperature
if( len(sys.argv) >= 2 ):
	draw.text((int(resX/4*3), int(resY/13*8)), sys.argv[2], font=font, fill='yellow', stroke_width=2)

image.show()
image.save(imageName)

print(imageName)
