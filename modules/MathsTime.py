# Python module for handling calculations for times and dates
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

from collections import OrderedDict 
import time
import datetime


def mathsForTime(hours, minutes):
	"""
	Wrapper function for datetime.timedelta() function
	"""
	return datetime.timedelta(0,0,0,0,minutes,hours,0)


def cTDelta():
	"""
	Returns time delta for current time
	"""
	currentTime = time.strftime("%H%M")
	cT_minutes = int(currentTime[-2:])
	cT_hours = int(currentTime[:-2])
	return mathsForTime(cT_hours, cT_minutes)

def calculateTimeDifference(time1, time2):
	"""
	Calculates the time difference for two time deltas
	and returns an additional value if the difference 
	is negative
	"""
	negative = False

	absoluteDifference = abs(time1 - time2)
	relativeDifference = time1 - time2
	
	if str(relativeDifference)[0:1] == '-':
		negative = True
	else:
		negative = False
	return absoluteDifference, negative

def buildArrivalTimeDeltaList(busArrivalTimes):
	"""
	Builds a list containing relative time deltas for the
	bus arrival times returned from TfL Bus Arrivals API
	"""
	
	arrivalTimesDelta = []
	for time in busArrivalTimes:
		arrivalTimesDelta.append(mathsForTime(0,time) +cTDelta())

	return arrivalTimesDelta

def queryCandidateTimes(arrivalTimesDelta, idealTime):
	"""
	Returns a sorted list of absolute arrival times, sorted in ascending
	order for the relative difference from the ideal time.
	Ideal time is defined as the set alarm time with the head start 
	in minutes added to this time.
	"""
	currTime = cTDelta()
	differenceTimes = {}

	# Creates a dictionary with keys storing the relative time difference
	# between the ideal time and the bus arrival times.
	# The values store the absolute bus arrival time for the given key.
	for time in arrivalTimesDelta:
		#absoluteValue, negative = calculateTimeDifference(idealTime, time)
		differenceTimes[abs(idealTime - time)] = time

	# Create a sorted list of differenceTimes in ascending order
	sortedDifferenceTimes = sorted(differenceTimes.keys())
	#sortedDifferenceTimes = sorted(differenceTimes, key=lambda x:int(str(abs(differenceTimes[x]))[:-2].replace(':','')))
	
	# Create an ordered dictionary mapping the relative time difference from 
	# the ideal time, to the absolute bus arrival times.
	# Sorted according to smallest time difference.
	sortedTimes = OrderedDict()
	for entry in sortedDifferenceTimes:
		sortedTimes[entry] = differenceTimes[entry]

	print("Querying bus arrival times:")
	for k,v in sortedTimes.items():
		print("Difference: %s, Arrival time: %s" % (str(k),str(v)))
	return sortedTimes


	
