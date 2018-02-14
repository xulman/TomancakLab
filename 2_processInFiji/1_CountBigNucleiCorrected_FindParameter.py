#@int(label="A nucleus is everything  BIGGER than (um^2)") areaMin
#@int(label="A nucleus is everything SMALLER than (um^2)") areaMax
#@boolean (label="Filter according to area") filterArea
#
#@float(label="A nucleus has a circularity  BIGGER than (lower value means higher circularity)") circularityMin
#@float(label="A nucleus has a circularity SMALLER than (lower value means higher circularity)") circularityMax
#@boolean (label="Filter according to circularity") filterCirc
#
#@boolean (label="Input image shows nuclei (checked) or membranes (unchecked) ") inputImageShowsNuclei
#@File (label="Pixel areas map:") aMapFile
#@File (label="X coordinate map:") xMapFile
#@File (label="Y coordinate map:") yMapFile
#@File (label="Z coordinate map:") zMapFile
#
#@boolean (label="Show sheet with analysis data") showRawData

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
sys.path.append(os.path.dirname(inspect.getfile(inspect.currentframe()))+"/lib")

# import our "library scripts"
from importsFromImSAnE import *
from chooseNuclei import *

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
	nuclei += findComponents(imp,backgroundPixelValue,realSizes,realCoordinates,"n_")

	# ------- analysis starts here -------
	circularitySum = 0
	sizesum = 0

	for nucl in nuclei:
		circularitySum += nucl.Circularity
		sizesum += nucl.Area

	print("Average Circularity: "+str(circularitySum/len(nuclei)))
	print("Average Area: "+str(sizesum/len(nuclei))+" square microns")

	print("Creating output image ...")
	OutputPixels = [[0 for y in range(imp.width)] for x in range(imp.height)]
	# green - fit both conditions
	# blue - does not fit area
	# white - does not fit circularity
	# red - fails both conditions
	#
	for nucl in nuclei:
		errCnt = 0
		if (filterCirc == True and (nucl.Circularity < circularityMin or nucl.Circularity > circularityMax)):
			errCnt += 1
		if (filterArea == True and (nucl.Area < areaMin or nucl.Area > areaMax)):
			errCnt += 2

		for pix in nucl.Pixels:
			OutputPixels[pix[1]][pix[0]] = colors[errCnt]

	OutputPixelsNew = reduce(lambda x,y :x+y ,OutputPixels)
	cp = ColorProcessor(imp.getWidth(),imp.getHeight(), OutputPixelsNew)
	OutputImg = ImagePlus("OutputImg", cp)
	OutputImg.show()


	# VLADO PROPER CIRC DEBUG
	for nucl in nuclei:
		nucl.DrawValue = nucl.Circularity*1000.0
	#drawChosenNucleiValue(imp.getWidth(),imp.getHeight(), nuclei)
	# VLADO PROPER CIRC DEBUG

	# VLADO PIXEL CIRC DEBUG
	for nucl in nuclei:
		nucl.DrawValue = abs(nucl.Size - ((nucl.EdgeSize**2)/(4*math.pi)))/nucl.Size
		nucl.DrawValue *= 1000.0
	#drawChosenNucleiValue(imp.getWidth(),imp.getHeight(), nuclei)
	# VLADO PIXEL CIRC DEBUG


	if (showRawData):
		print("Populating table...")

		# create an output table with three columns: label, circularity, area, size, positionX, positionY
		rt = ResultsTable()

		# also create two hidden 1D images (arrays essentially) and ask to display their histograms later
		imgArea = []
		imgCirc = []

		for nucl in nuclei:
			rt.incrementCounter()
			rt.addValue("label"                            ,nucl.Color)
			rt.addValue("circularity (lower more roundish)",nucl.Circularity)
			rt.addValue("circularity (pixel-based)"        ,nucl.DrawValue) # VLADO PIXEL CIRC DEBUG
			rt.addValue("area (um^2)"                      ,nucl.Area)
			rt.addValue("area (px)"                        ,nucl.Size)
			rt.addValue("centreX (px)"                     ,nucl.CentreX)
			rt.addValue("centreY (px)"                     ,nucl.CentreY)

			imgArea.append(nucl.Area)
			imgCirc.append(nucl.Circularity)

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


	print("Done.")


main()
