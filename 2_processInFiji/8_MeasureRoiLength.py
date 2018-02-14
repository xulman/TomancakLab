#@File (label="X coordinate map:") xMapFile
#@File (label="Y coordinate map:") yMapFile
#@File (label="Z coordinate map:") zMapFile

from ij import IJ
from ij.gui import PolygonRoi, Roi
from ij.measure import ResultsTable
import math

# this section adds a folder, in which this very script is living,
# to the current search paths so that we can import our "library script"
import sys.path
import os.path
import inspect
sys.path.append(os.path.dirname(inspect.getfile(inspect.currentframe()))+"/lib")

# import our "library script"
from importsFromImSAnE import *
from properMeasurements import *


#Calculate the 'real Coordinates', that take into account the different pixel sizes
realCoordinates = readRealCoords(xMapFile.getAbsolutePath(),yMapFile.getAbsolutePath(),zMapFile.getAbsolutePath());

# Get current ImagePlus
image = IJ.getImage();

# check the compatibility...
checkSize2DarrayVsImgPlus(realCoordinates,image)

def reportInterpolatedPoints(coords, x1,y1, x2,y2):
	dx = x2-x1
	dy = y2-y1
	length = math.sqrt(dx*dx + dy*dy)

	# how many 0.1 long intervals fit into the whole vector
	steps = int(math.ceil(length*10.0))
	for step in range(steps):
		x=x1 + dx*float(step)/steps
		y=y1 + dy*float(step)/steps
		coords.append([x,y])
	# NB: the [x2,y2] will be written as the first point of the next segment

def collectAndReportPoints():
	# Get current ROI, i.e. from the current slice
	roi = image.getRoi()

	if roi is not None:
		# Get ROI points
		polygon = roi.getPolygon()
		x = polygon.xpoints
		y = polygon.ypoints

		coords = []

		#... and report them
		for i in range(1,polygon.npoints):
			reportInterpolatedPoints(coords, x[i-1],y[i-1], x[i],y[i])

		# report also the very last point
		coords.append([x[polygon.npoints-1],y[polygon.npoints-1]])
		print "Coordinates processed for frame "+str(image.getSlice())
		return coords
	else:
		print "No ROI is available for frame "+str(image.getSlice())
		return []


# scan through all slices of the image and report respective ROIs
table = ResultsTable()
#for z in range(1,2):
for z in range(1,image.getNSlices()+1):
	image.setSlice(z)
	coords = collectAndReportPoints()
	if (len(coords) > 0):
		table.incrementCounter()
		table.addValue('Slice no.',z)
		table.addValue('Proper Length',properLength(coords,realCoordinates))
table.show('Results')

