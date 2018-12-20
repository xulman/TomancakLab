#@File (style="directory", label="Folder with maps:") mapFolder
class SimpleFile:
	def __init__(self,path):
		self.path = path
	def getAbsolutePath(self):
		return self.path

aMapFile = SimpleFile(mapFolder.getAbsolutePath()+"/cylinder1_area.txt")
xMapFile = SimpleFile(mapFolder.getAbsolutePath()+"/cylinder1coords_X.txt")
yMapFile = SimpleFile(mapFolder.getAbsolutePath()+"/cylinder1coords_Y.txt")
zMapFile = SimpleFile(mapFolder.getAbsolutePath()+"/cylinder1coords_Z.txt")


# Usage:
#	- Run Fiji
# 	- Make sure that the update site SCF-MPI-CBG is activated
#	- Open one representative image of your data
#	- Run this script
# 	- If you are not confident with the output, repeat with other parameters.

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


# reads the area_per_pixel information, already in squared microns
realSizes = readRealSizes(aMapFile.getAbsolutePath())

# read the 'real Coordinates', that take into account the different pixel sizes
realCoordinates = readRealCoords(xMapFile.getAbsolutePath(),yMapFile.getAbsolutePath(),zMapFile.getAbsolutePath())


def main():
	w = len(realSizes)
	h = len(realSizes[0])
	print("calculating from maps in the folder: "+mapFolder.getAbsolutePath())
	print("width="+str(w)+", heigh="+str(h))

	OutputPixels = [ 0.0 for o in range(w*h) ]

	# x sizes
	histData = []
	for y in range(2,h-2):
		for x in range(2,w-2):
			coords = [ [x,y], [x+1,y] ]
			length = properLength(coords, realCoordinates)

			OutputPixels[y*w +x] = length
			histData.append(length)

	ImagePlus("X: 1px distances", FloatProcessor(w,h, OutputPixels)).show()

	histImg = ImagePlus("X: 1px distances",FloatProcessor(len(histData),1,histData))
	IJ.run(histImg, "Histogram", "100")

	print("BTW: there are "+str(len(histData))+" lengths for the histograms")


	histData = []
	for y in range(2,h-2):
		for x in range(2,w-2):
			coords = [ [x,y], [x,y+1] ]
			length = properLength(coords, realCoordinates)

			OutputPixels[y*w +x] = length
			histData.append(length)

	ImagePlus("Y: 1px distances", FloatProcessor(w,h, OutputPixels)).show()

	histImg = ImagePlus("Y: 1px distances",FloatProcessor(len(histData),1,histData))
	IJ.run(histImg, "Histogram", "100")


main()
