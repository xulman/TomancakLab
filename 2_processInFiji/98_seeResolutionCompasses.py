#@File (style="directory", label="Folder with maps:") mapFolder
#@String (label="Choose comma-separated orientations from N,NE,E,SE,S,SW,W,NW:", value="N,NE,E,SE,S,SW,W,NW") dirSides
#@int (label="Pixel length of all sides of the compass:", value="3", min="1") dirLength
#@int (label="Distance between compasses along axis X:", min="1", value="20") xGridStep
#@int (label="Distance between compasses along axis Y:", min="1", value="20") yGridStep
#@int (label="Position of 1st compass from top-left along axis X:", min="1", value="5") xGridInit
#@int (label="Position of 1st compass from top-left along axis Y:", min="1", value="5") yGridInit

class SimpleFile:
	def __init__(self,path):
		self.path = path
	def getAbsolutePath(self):
		return self.path

aMapFile = SimpleFile(mapFolder.getAbsolutePath()+"/cylinder1_area.txt")
xMapFile = SimpleFile(mapFolder.getAbsolutePath()+"/cylinder1coords_X.txt")
yMapFile = SimpleFile(mapFolder.getAbsolutePath()+"/cylinder1coords_Y.txt")
zMapFile = SimpleFile(mapFolder.getAbsolutePath()+"/cylinder1coords_Z.txt")

from ij import IJ
from ij import ImagePlus
from ij.process import FloatProcessor

# this section adds a folder, in which this very script is living,
# to the current search paths so that we can import our "library script"
import sys.path
import os.path
import inspect
ScriptsRoot = os.path.dirname(os.path.dirname(sys.path[0]))+os.sep+"scripts"
ThisFile    = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.append(ScriptsRoot+os.sep+ThisFile+os.sep+"lib")
sys.path.append(ThisFile+os.sep+"lib")

# import our "library scripts"
from importsFromImSAnE import *
from properMeasurements import *

compass={}
compass[ 'N'] = [ 0,-1, 0]
compass['NE'] = [+1,-1, 1]
compass[ 'E'] = [+1, 0, 2]
compass['SE'] = [+1,+1, 3]
compass[ 'S'] = [ 0,+1, 4]
compass['SW'] = [-1,+1, 5]
compass[ 'W'] = [-1, 0, 6]
compass['NW'] = [-1,-1, 7]
#                dx,dy, index


def parsingSides(dirSides):
	seenSides = set()
	directions = []

	sides = dirSides.split(',',20)
	for side in sides:
		sside = side.strip()

		#    a side?       &     known side?    &  not already processed?
		if len(sside) > 0 and sside in compass and sside not in seenSides:
			print("Found side: "+sside)

			seenSides.add(sside)
			directions.append(compass[sside])

	return directions


def main():
	# reads the area_per_pixel information, already in squared microns
	realSizes = readRealSizes(aMapFile.getAbsolutePath())

	# read the 'real Coordinates', that take into account the different pixel sizes
	realCoordinates = readRealCoords(xMapFile.getAbsolutePath(),yMapFile.getAbsolutePath(),zMapFile.getAbsolutePath())

	w = len(realSizes)
	h = len(realSizes[0])
	print("calculating from maps in the folder: "+mapFolder.getAbsolutePath())
	print("width="+str(w)+", heigh="+str(h))

	directions = parsingSides(dirSides)

	# how many pixels in diagonal directions
	diaLength = int( math.floor( float(dirLength)/1.41421 +0.5 ) )
	direSteps = [dirLength,diaLength,dirLength,diaLength,dirLength,diaLength,dirLength,diaLength]
	# 'direSteps' must match the index column in the 'compass'

	print("horiz/vert arm pixels: "+str(dirLength))
	print(" diagonal  arm pixels: "+str(diaLength)+"   (yields length of "+str(1.41421*float(diaLength))+")")

	OutputPixels = [ 0.0 for o in range(w*h) ]

	# smallest and largest length spotted
	minLength = 10000000;
	maxLength = 0;

	# grid positions
	for y in range(2+yGridInit, h-2, yGridStep):
		for x in range(2+xGridInit, w-2, xGridStep):
			for dire in directions:
				# skip the first element (the centre)
				coords = []

				# add the sides/arms
				cx = x
				cy = y
				for i in range(direSteps[dire[2]]):
					cx += dire[0]
					cy += dire[1]
					coords.append( [cx,cy] )

				length = properLength(coords, realCoordinates)
				minLength = min(length,minLength)
				maxLength = max(length,maxLength)

				for px in coords:
					OutputPixels[px[1]*w +px[0]] = length

			# black centre (because it is shared, hence it does not belong to anyone)
			#OutputPixels[y*w +x] = 0

	ImagePlus("Resolution compasses", FloatProcessor(w,h, OutputPixels)).show()

	print("the smaller micron length of a bar is: "+str(minLength))
	print("the largest micron length of a bar is: "+str(maxLength))


main()
