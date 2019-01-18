from __future__ import print_function
#@File (label="Input Mamuth XML file:") xmlFile
#@String (label="Draw only up to these time points (e.g. 1-5,7,9):") drawAtTheseTimepoints
#@File (label="Output trajectories TIFF file:") tifFile
#@int (label="Original image X size:") xSize
#@int (label="Original image Y size:") ySize
#@int (label="Original image Z size:") zSize
#@boolean (label="Squash everything to 2D:") shouldDoTwoD
#@int (label="Downsampling factor:") xDown
#@int (label="Thickness of trajectories in pixels:") trackThickness

from ij import IJ
import ij.ImagePlus
import ij.ImageStack
from ij.process import ShortProcessor
import math

# this section adds a folder, in which this very script is living,
# to the current search paths so that we can import any script living next to this one
import sys.path
import os.path
import inspect
ScriptsRoot = os.path.dirname(os.path.dirname(sys.path[0]))+os.sep+"scripts"
ThisFile    = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.append(ScriptsRoot+os.sep+ThisFile+os.sep+"lib")
sys.path.append(ThisFile+os.sep+"lib")
from MamutXMLreader import *
from tools import *


# adjust the size of the output image immediately
Down = float(xDown)
xSize = int(math.ceil(xSize / Down))
ySize = int(math.ceil(ySize / Down))
zSize = int(math.ceil(zSize / Down))

if shouldDoTwoD:
	zSize = 1

# ------------------------------------------------------------------------------------
# labels are of this form: trackID*SEPARATOR + (timePoint-TSHIFT)
# requirements:
#   trackID has to start from 0 or 1, should not be too many of them
#   the time interval must not be longer than SEPARATOR

# dividing by SEPARATOR (e.g. via Image->Math) one can strip away time information/coordinate;
# thresholding by 1, one can strip away all tracking information (track ID, time coordinate)
SEPARATOR = 0

# ------------------------------------------------------------------------------------
# draws a line made of many (overlapping) balls, of width R from
# spotA to spotB that belongs to track ID, into the image, but
# don't draw no further than given stopTime; the TSHIFT is a helping
# parameter connected to the SEPARATOR
def drawLine(spotA,spotB,stopTime, R,ID,TSHIFT,img):
	xC = spotA[0]
	yC = spotA[1]
	zC = spotA[2]
	xD = spotB[0]
	yD = spotB[1]
	zD = spotB[2]

	if shouldDoTwoD:
		zC = 0
		zD = 0

	# the final color becomes Col+deltaTime
	Col = ID*SEPARATOR +spotA[3] -TSHIFT

	# the line length (LL)
	LL = math.sqrt((xC-xD)*(xC-xD) + (yC-yD)*(yC-yD) + (zC-zD)*(zC-zD))

	# how many up-to-R-long segments are required
	SN = math.ceil(LL / R)

	# if "line is decimated into a point", just draw one spot
	if SN == 0:
		drawBall(xC,yC,zC,R*Down,Col,img,Down)
		# NB: the coordinates and _radius_ will get divided by Down,
		#     but we want R to represent already the final radius
		return

	# (real) length of one segment
	SS = LL / SN

	# a "one segment" vector
	xSV = (xD-xC)*SS/LL
	ySV = (yD-yC)*SS/LL
	zSV = (zD-zC)*SS/LL

	# similarily for time
	deltaT = float(spotB[3]-spotA[3]) / SN

	# shortcut... makes stopTime relative to the time of the spotA
	stopTime = stopTime - spotA[3]

	SN = int(SN)
	for i in range(0,SN+1):
		# don't draw beyond the stopTime
		if i*deltaT > stopTime:
			return

		x = xC  +  float(i)*xSV
		y = yC  +  float(i)*ySV
		z = zC  +  float(i)*zSV

		drawBall(x,y,z,R*Down,Col+int(i*deltaT),img,Down)


# ------------------------------------------------------------------------------------
# the main work happens here
def main(timePointList):

	# --- this parses the data in ---
	[minT,maxT] = readInputXMLfile(xmlFile.getAbsolutePath())

	# now, we have a list of roots & we have neighborhood-ships,
	# let's reconstruct the trees from their roots,
	# in fact we do a depth-first search...
	lastID = 0
	for root in ROOTS:
		print("extracted tree ID="+str(root))
		lastID = followTrack(ROOTS[root],lastID+1)
	# --- this parses the data in ---


	# create the output image (only once cause it is slow)
	outShortProcessors = [ ShortProcessor(xSize,ySize) for z in range(zSize) ]
	img = [ outShortProcessors[z].getPixels() for z in range(len(outShortProcessors)) ]

	stack = ij.ImageStack(xSize,ySize)
	for sp in outShortProcessors:
		stack.addSlice(sp)

	# create the wrapping data structure...
	simpleImg = SimpleImg(img,xSize,ySize,zSize)

	# now: 'img' is an array of arrays that essentially shadow the pixel data
	# from the 'stack' (ImageStack that has been built around 'img'),
	# and 'simpleImg' only wraps (holds it) around the 'img'

	outImp = ij.ImagePlus("trajectories", stack)
	outImp.show()
	#NB: the img is essentially a "python overlay" over the IJ1 image stack's pixel data

	print("detected interval of time points ["+str(minT)+","+str(maxT)+"]")


	for maxDrawTime in timePointList:
		simpleImg.setPixelsToZero()

		# scan all tracks
		for tID in TRACKS:
			TRACK = TRACKS[tID]

			# create consecutive pairs of time points
			tA = minT-1
			for tB in sorted(TRACK.keys()):
				if tA >= minT:
					# consecutive pair (tA,tB)

					#print("track "+str(tID)+": time pair "+str(tA)+" -> "+str(tB))

					spotA = SPOTS[TRACK[tA]]
					if spotA[3] < maxDrawTime:
						spotB = SPOTS[TRACK[tB]]
						drawLine(spotA,spotB,maxDrawTime, trackThickness, tID,minT, simpleImg)

				tA = tB


		# now write the image onto harddrive...
		fn = tifFile.getAbsolutePath()
		i = fn.rfind('.')
		fn = fn[0:i]+str(maxDrawTime)+fn[i:len(fn)]

		print("Writing trajectory image: "+fn)
		IJ.save(outImp,fn)


try:
	tpList = parseOutTimes(drawAtTheseTimepoints);
	main(tpList)
except ValueError as ve:
	print(ve)

