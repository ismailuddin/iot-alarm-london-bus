# Internet of Things TfL bus stop alarm clock with a Raspberry Pi
# www.scienceexposure.com

# Copyright 2015 Ismail Uddin

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
from threading import Thread
import datetime
from modules.buzzer import *
from modules.MathsTime import *
from Adafruit_IO import Client
import RPi.GPIO as GPIO
from TfLAPI.LondonBusAPI import *

#Initialise GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialise Adafruit IO client
adafruitIOKey = ''
aio = Client(adafruitIOKey)

# Initialise TfL Bus Arrivals API
tfl = TfLBusArrivalsAPI()

# Collect information for setting up IoT alarm
busLine = raw_input("Please input the bus number you need to catch: \n")
busStop = raw_input("Please input the bus stop code for your bus stop: \n")
alarmTime = raw_input("Please input what time you normally expect to wake up at (HHMM): \n")
headStart = raw_input("Please input how many minutes do you need after waking up to catch your bus: \n")

print("Alarm has been set for %s hrs, to catch the %s bus. %s minutes has been set to reach the bus stop. \n" % (alarmTime, busLine, headStart))
print("If your bus is delayed more than %s minutes, the alarm will be delayed to wake you up and still give you the same time to get ready." % headStart)

# Initialise currentTime variable
currentTime = cTDelta()

# Set up time deltas
aT_minutes = str(alarmTime)[-2:]
aT_hours = str(alarmTime)[:-2]
alarmTimeDelta = mathsForTime(int(aT_hours), int(aT_minutes))
hSDelta = mathsForTime(0,int(headStart))

# Boolean parameters
main = True
buzzingBool = 0

# Time update loop
def timeUpdateLoop():
	global currentTime
	while True:
		currentTime = cTDelta()

# Loop to continuously update time as a time delta
def mainLoop():
	global alarmTimeDelta

	# Create list of time deltas for absolute bus arrival times
	arrivalTimes = tfl.queryBusArrivals(bus_line="%s" % busLine, bus_stop_code=busStop)
	arrivalTimesDelta = buildArrivalTimeDeltaList(arrivalTimes)

	while main == True:
		idealTime = alarmTimeDelta + hSDelta
		print("Ideal time to for a bus to arrive at is: %s" % idealTime)
		differenceFromAlarm = (alarmTimeDelta - currentTime).seconds
		if differenceFromAlarm <= 1800:
			sDT = queryCandidateTimes(arrivalTimesDelta, idealTime)
			bestArrivalTime = sDT.values()[0]
			print("Best bus arrival time: %s" % str(bestArrivalTime))
			alarmTimeDelta = bestArrivalTime - hSDelta
			print("Alarm time altered to: %s" % alarmTimeDelta)
		else:
			pass
		print("Current time is: %s" % currentTime)
		time.sleep(45)


# Loop to continuously check to buzz the buzzer at the set alarm time
def alarmBuzzLoop():
	global buzzingBool
	while True:
		cT = int(str(currentTime)[:-3].replace(':',''))
		aTD = int(str(alarmTimeDelta)[:-3].replace(':',''))
		if cT == aTD or buzzingBool == 1:
			buzz(10, 0.5)
			time.sleep(0.25)
			buzz(20,0.5)
			time.sleep(0.25)
			buzzingBool = 1
			aio.send('iot-alarm', 'Alarm time!')
			print("Alarm time is %s" % aTD)
			print("Wake up to catch the %s on time!" % busLine)
		time.sleep(1.25)

# Loop for snooze button
def snoozeLoop():
	global buzzingBool
	global alarmTimeDelta
	global main

	while True:
		if GPIO.input(25) == 0 and buzzingBool == 1:
			alarmTimeDelta = mathsForTime(0,8) + alarmTimeDelta
			buzzingBool = 0
			main = False
			print("Alarm delayed by 8 minutes to %s." % str(alarmTimeDelta))
		else:
			pass
		time.sleep(0.5)


try:
	t1 = Thread(target=timeUpdateLoop)
	t2 = Thread(target=mainLoop)
	t3 = Thread(target=alarmBuzzLoop)
	t4 = Thread(target=snoozeLoop)
	threads = [t1,t2,t3, t4]
	for thread in threads:
		thread.daemon = True
		thread.start()
	while True:
		time.sleep(100)

except (KeyboardInterrupt, SystemExit):
	print("End")
