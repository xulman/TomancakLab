#@int(label="A nucleus is everything  BIGGER than (um^2)") areaMin
#@int(label="A nucleus is everything SMALLER than (um^2)") areaMax
#@boolean (label="Filter according to area") filterArea
#
#@float(label="A nucleus has a circularity  BIGGER than (1 represents perfect circularity)") circularityMin
#@float(label="A nucleus has a circularity SMALLER than (1 represents perfect circularity)") circularityMax
#@boolean (label="Filter according to circularity") filterCirc
#
#@boolean (label="Input image shows nuclei (checked) or membranes (unchecked) ") inputImageShowsNuclei
#@File (style="directory", label="Folder with maps:") mapFolder
class SimpleFile:
	def __init__(self,path):
		self.path = path
	def getAbsolutePath(self):
		return self.path

aMapFile = SimpleFile(mapFolder.getAbsolutePath()+"/cylinder2_area.txt")
xMapFile = SimpleFile(mapFolder.getAbsolutePath()+"/cylinder2coords_X.txt")
yMapFile = SimpleFile(mapFolder.getAbsolutePath()+"/cylinder2coords_Y.txt")
zMapFile = SimpleFile(mapFolder.getAbsolutePath()+"/cylinder2coords_Z.txt")

#
#@boolean (label="Show sheet with analysis data") showRawData
#@boolean (label="Show image with areas") showAreaImage
#@boolean (label="Show image with circularities") showCircImage
#@boolean (label="Show image with shape factors") showShapeFactorImage
#@boolean (label="Show image with neighbor counts") showNeigImage

# This script should be used to find suitable parameters for CountBigNucleiCorrected.py
# You'll see nuclei of various colors:
# green - fit both conditions      (area good, circularity good)
# white - does not fit circularity (area good, circularity bad)
# blue - does not fit area         (area bad,  circularity good)
# red - fails both conditions      (area bad,  circularity bad)
colors = [0x00FF00, 0xFFFFFF, 0x0000FF, 0xFF0000]

# Usage:
#	- Run Fiji
# 	- Make sure that the update site SCF-MPI-CBG is activated
#	- Open one representative image of your data
#	- Run this script
# 	- If you are not confident with the output, repeat with other parameters.

from ij import IJ
from ij import ImagePlus
from ij.process import ColorProcessor
from ij.process import FloatProcessor
from ij.measure import ResultsTable

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
from chooseNuclei import *
from properMeasurements import *

# import the same Nucleus class to make sure the very same calculations are used
from Nucleus import Nucleus

# VLADO PROPER CIRC DEBUG
# VLADO PIXEL CIRC DEBUG
import math


# reads the area_per_pixel information, already in squared microns
realSizes = readRealSizes(aMapFile.getAbsolutePath())

# read the 'real Coordinates', that take into account the different pixel sizes
realCoordinates = readRealCoords(xMapFile.getAbsolutePath(),yMapFile.getAbsolutePath(),zMapFile.getAbsolutePath())

imp = IJ.getImage()


def main():
	# test that sizes of realSizes and imp matches
	checkSize2DarrayVsImgPlus(realSizes, imp)
	checkSize2DarrayVsImgPlus(realCoordinates, imp)

	backgroundPixelValue = 1 # in case of cell nuclei
	if (not inputImageShowsNuclei):
		backgroundPixelValue = 2 # in case of cell membranes

	# obtain list of all valid nuclei
	nuclei = chooseNuclei(imp,backgroundPixelValue,realSizes,realCoordinates, filterArea,areaMin,areaMax, filterCirc,circularityMin,circularityMax)
	# add list of all INvalid nuclei (since only invalid are left in the input image)
	#nuclei += findComponents(imp,backgroundPixelValue,realSizes,realCoordinates,"n_")

	# ------- analysis starts here -------
	circularitySum = 0
	sizesum = 0

	i = IJ.getImage().getProcessor().getPixels()
	w = IJ.getImage().getWidth()

	for nucl in nuclei:
		circularitySum += nucl.Circularity
		sizesum += nucl.Area
		nucl.setNeighborsList(i,w)

	print("Average Circularity: "+str(circularitySum/len(nuclei)))
	print("Average Area: "+str(sizesum/len(nuclei))+" square microns")


	if showCircImage:
		for nucl in nuclei:
			nucl.DrawValue = nucl.Circularity
		drawChosenNucleiValue("Real circularities", imp.getWidth(),imp.getHeight(), nuclei)

	if showShapeFactorImage:
		for nucl in nuclei:
			nucl.DrawValue = nucl.ShapeFactor
		drawChosenNucleiValue("Real shape factors", imp.getWidth(),imp.getHeight(), nuclei)

	if showAreaImage:
		for nucl in nuclei:
			nucl.DrawValue = nucl.Area;
		drawChosenNucleiValue("Real areas", imp.getWidth(),imp.getHeight(), nuclei)

	if showNeigImage:
		for nucl in nuclei:
			nucl.DrawValue = len(nucl.NeighIDs);
		drawChosenNucleiValue("Neighborhood counts", imp.getWidth(),imp.getHeight(), nuclei)


	if (showRawData):
		print("Populating table...")

		# create an output table with three columns: label, circularity, area, size, positionX, positionY
		rt = ResultsTable()

		# also create two hidden 1D images (arrays essentially) and ask to display their histograms later
		imgArea = []
		imgCirc = []
		imgNeig = []

		for nucl in nuclei:
			rt.incrementCounter()
			rt.addValue("label"                            ,nucl.Color)
			rt.addValue("circularity (higher more roundish)",nucl.Circularity)
			rt.addValue("circularity (pixel-based)"        ,nucl.DrawValue) # VLADO PIXEL CIRC DEBUG
			rt.addValue("shape factor"                     ,nucl.ShapeFactor)
			rt.addValue("area (um^2)"                      ,nucl.Area)
			rt.addValue("area (px)"                        ,nucl.Size)
			rt.addValue("perimeter (px)"                   ,nucl.EdgeSize)
			rt.addValue("perimeter (um)"                   ,nucl.EdgeLength)
			rt.addValue("neigbor count"                    ,len(nucl.NeighIDs))
			rt.addValue("centreX (px)"                     ,nucl.CentreX)
			rt.addValue("centreY (px)"                     ,nucl.CentreY)

			imgArea.append(nucl.Area)
			imgCirc.append(nucl.Circularity)
			imgNeig.append(len(nucl.NeighIDs))

		# show the image
		rt.showRowNumbers(False)
		rt.show("Nuclei properties")

		# show the histograms
		#imgArea = ImagePlus("areas of nuclei",FloatProcessor(len(nuclei),1,imgArea))
		imgArea = ImagePlus("nuclei_areas",FloatProcessor(len(nuclei),1,imgArea))
		IJ.run(imgArea, "Histogram", str( (imgArea.getDisplayRangeMax() - imgArea.getDisplayRangeMin()) / 10 ))

		#imgCirc = ImagePlus("circularities of nuclei",FloatProcessor(len(nuclei),1,imgCirc))
		imgCirc = ImagePlus("nuclei_circularities",FloatProcessor(len(nuclei),1,imgCirc))
		IJ.run(imgCirc, "Histogram", "20")

		imgNeig = ImagePlus("nuclei_neigborCount",FloatProcessor(len(nuclei),1,imgNeig))
		IJ.run(imgNeig, "Histogram", "10")

		# debug: what perimeter points are considered
		# writeCoordsToFile(nuclei[0].EdgePixels,"/Users/ulman/DATA/fp_coords_0.txt")
		# writeCoordsToFile(nuclei[1].EdgePixels,"/Users/ulman/DATA/fp_coords_1.txt")


	print("Done.")


main()
