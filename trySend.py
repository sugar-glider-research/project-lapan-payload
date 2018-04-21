from picamera import PiCamera
from cv2 import imread
from time import sleep
import serial
import numpy as np
from tryCompres import compress

width = 200
height = 200
dataArray = np.empty((height,((width*3)+2)), dtype=np.uint8)
redArray = np.empty((height,(width+2)), dtype=np.uint8)
greenArray = np.empty((height,(width+2)), dtype=np.uint8)
blueArray = np.empty((height,(width+2)), dtype=np.uint8)
compArray = np.empty((height,width), dtype=np.uint8)

#capture
with PiCamera() as camera:
	camera.resolution = [width,height]
	sleep(0.1)
	camera.capture('image.bmp')

#serial
serPort = serial.Serial(   
	port = '/dev/ttyUSB0',
	baudrate = 57600,
	parity = serial.PARITY_NONE,
	stopbits = serial.STOPBITS_ONE,
	bytesize = serial.EIGHTBITS,
	timeout = 1
)
	
#extract
imageArray = imread('image.bmp')

#build and send data versi 1 : 3 channel raw
#dataArray[:,0] = 255
#dataArray[:,((width*3)+1)] = 10
#for line in range (0,height):
#	for byte in range (0,width):
#		for chan in range (1,4):
#			#scaling versi 1
#			#dataArray[line,((byte*3)+chan)] = np.interp(imageArray[line,byte,(chan-1)], [0,255], [33,254])
#			#scaling versi 2
#			dataArray[line,((byte*3)+chan)] = np.floor(imageArray[line,byte,(chan-1)]/2)+127
#	serPort.flushInput()
#	serPort.flushOutput()
#	serPort.write(dataArray[line])
#	print dataArray[line]
#	sleep(0.3)

#build and send data versi 2 : 1 channel raw
#redArray[:,0] = 255
#redArray[:,(width+1)] = 10
#for line in range (0,height):
#        for byte in range (0,width):
#	        redArray[line,(byte+1)] = np.floor(imageArray[line,byte,0]/2)+127
#        serPort.flushInput()
#        serPort.flushOutput()
#        serPort.write(redArray[line])
#        print redArray[line]
#        sleep(0.1)

#build and send data versi 3 : 1 channel jpeg
for line in range (0,height):
        for byte in range (0,width):
		compArray[line,byte] = imageArray[line,byte,0]

compress(compArray)
