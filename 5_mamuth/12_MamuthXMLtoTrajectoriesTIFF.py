from __future__ import print_function
#@File (label="Input Mamuth XML file:") xmlFile
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
ThisFile    = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(ScriptsRoot+ThisFile+os.sep+"lib")
sys.path.append(ThisFile+os.sep+"lib")
from MamutXMLreader import *


# adjust the size of the output image immediately
Down = float(xDown)
xSize = int(math.ceil(xSize / Down))
ySize = int(math.ceil(ySize / Down))
zSize = int(math.ceil(zSize / Down))

if shouldDoTwoD:
	zSize = 1


# labels are of this form: trackID*SEPARATOR + (timePoint-TSHIFT)
# requirements:
#   trackID has to start from 0 or 1, should not be too many of them
#   the time interval must not be longer than SEPARATOR

# dividing by SEPARATOR (e.g. via Image->Math) one can strip away time information/coordinate;
# thresholding by 1, one can strip away all tracking information (track ID, time coordinate)
SEPARATOR = 100

# ------------------------------------------------------------------------------------
# draws a line made of many (overlapping) balls, of width R from
# spotA to spotB that belongs to track ID, into the image
def drawLine(spotA,spotB, R,ID,TSHIFT,img):
	# the coordinates will get divided by Down, and R as well;
	# in this function, however, we want R to represent already the final
	# width (radius), so we multiply by Down (to get divided later...)
	R = R * Down

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
		drawBall(xC,yC,zC,R,Col,img)
		return

	# (real) length of one segment
	SS = LL / SN

	# a "one segment" vector
	xSV = (xD-xC)*SS/LL
	ySV = (yD-yC)*SS/LL
	zSV = (zD-zC)*SS/LL

	# similarily for time
	deltaT = float(spotB[3]-spotA[3]) / SN

	SN = int(SN)
	for i in range(0,SN+1):
		x = xC  +  float(i)*xSV
		y = yC  +  float(i)*ySV
		z = zC  +  float(i)*zSV

		drawBall(x,y,z,R,Col+int(i*deltaT),img)


# ------------------------------------------------------------------------------------
# draws ball of radius R with center xC,yC,zC with colour Col into the image
def drawBall(xC,yC,zC,R,Col,img):
	xC = int(math.ceil(xC / Down))
	yC = int(math.ceil(yC / Down))
	zC = int(math.ceil(zC / Down))
	R  = int(math.ceil(R  / Down))

	if shouldDoTwoD:
		zC = 0

	#print("SPOT: "+str(xC)+","+str(yC)+","+str(zC)+" r="+str(R)+" @ ID="+str(Col))

	x_min = xC-R if xC > R       else 0
	x_max = xC+R if xC+R < xSize else xSize-1

	y_min = yC-R if yC > R       else 0
	y_max = yC+R if yC+R < ySize else ySize-1

	z_min = zC-R if zC > R       else 0
	z_max = zC+R if zC+R < zSize else zSize-1

	R2 = R*R

	# sweep the bounds and draw the ball
	for x in range(x_min,x_max+1):
		dx = (x-xC) * (x-xC)

		for y in range(y_min,y_max+1):
			dxy = dx + ((y-yC) * (y-yC))

			for z in range(z_min,z_max+1):
				dz = (z-zC) * (z-zC)

				if dxy+dz <= R2:
					img[z][x + y*xSize] = Col


# ------------------------------------------------------------------------------------
# the main work happens here
def main():

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

	outImp = ij.ImagePlus("trajectories", stack)
	outImp.show()
	#NB: the img is essentially a "python overlay" over the IJ1 image stack's pixel data

	print("detected interval of time points ["+str(minT)+","+str(maxT)+"]")


	# scan all tracks
	for tID in TRACKS:
		TRACK = TRACKS[tID]

		# create consecutive pairs of time points
		tA = minT-1
		for tB in sorted(TRACK.keys()):
			if tA >= minT:
				# consecutive pair (tA,tB)

				print("track "+str(tID)+": time pair "+str(tA)+" -> "+str(tB))

				spotA = SPOTS[TRACK[tA]]
				spotB = SPOTS[TRACK[tB]]
				drawLine(spotA,spotB, trackThickness, tID,minT, img)

			tA = tB


	# now write the image onto harddrive...
	print("Writing trajectory image: "+tifFile.getAbsolutePath())
	IJ.save(outImp,tifFile.getAbsolutePath())


main()
