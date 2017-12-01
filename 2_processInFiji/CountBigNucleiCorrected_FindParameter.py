#@int(label="A nucleus is everything  BIGGER than (um^2)", value=70) areaMin
#@int(label="A nucleus is everything SMALLER than (um^2)", value=130) areaMax
#@boolean (label="Filter according to area") filterArea
#
#@float(label="A nucleus has a circularity  BIGGER than (lower value means higher circularity)", value=0.3) circularityMin
#@float(label="A nucleus has a circularity SMALLER than (lower value means higher circularity)", value=0.7) circularityMax
#@boolean (label="Filter according to circularity") filterCirc
#
#@boolean (label="Input image shows nuclei (checked) or membranes (unchecked) ") inputImageShowsNuclei
#@File (label="Pixel areas map:") aMapFile
#
#@boolean (label="Show sheet with analysis data") showRawData

# This script should be used to find siutable parameters for CountBigNuclei.py
# You'll see:
# red nuclei   -- does not fit into circularity range
# blue nuclei  -- does not fit into area range
# white nuclei -- fit into both ranges

# Usage:
#	- Run Fiji
# 	- Make sure that the update site SCF-MPI-CBG is activated
#	- Open one representative image of your data
#	- Run this script
# 	- If you are not confident with the output, repeat with other parameters.

from ij import IJ
from ij import ImagePlus
import math
from ij.process import ColorProcessor 
from ij.measure import ResultsTable

# this section adds a folder, in which this very script is living,
# to the current search paths so that we can import our "library script"
import sys.path
import os.path
import inspect
sys.path.append(os.path.dirname(inspect.getfile(inspect.currentframe())))

# import our "library script"
from importsFromImSAnE import *

imp = IJ.getImage()
ip = imp.getProcessor()

# reads the area_per_pixel information, already in squared microns
realSizes = readRealSizes(aMapFile.getAbsolutePath());


class Nucleus:

	def __init__(self,Pixels,Color):
		# list of pixels that make up this nuclei (nuclei mask)
		self.Pixels = Pixels

		# label of the nuclei
		self.Color = Color

		# in squared microns
		self.area = 0.0
		# in pixel count
		self.size = len(Pixels)

		# geometric centre in pixel coordinates
		self.centreX = 0.0
		self.centreY = 0.0

		for pix in Pixels:
			self.area += realSizes[pix[0]][pix[1]]
			self.centreX += pix[0]
			self.centreY += pix[1]

		# finish calculation of the geometrical centre
		self.centreX /= len(Pixels)
		self.centreY /= len(Pixels)

		self.edgePixels = []
		for pix in Pixels:
			thisColor = ip.getPixel(pix[0],pix[1])
			try:
				ColorLeft = ip.getPixel(pix[0]-1,pix[1])
			except:
				ColorLeft = - 1

			try:
				ColorAbove = ip.getPixel(pix[0],pix[1]-1)
			except:
				ColorAbove = -1

			try:
				ColorBelow = ip.getPixel(pix[0],pix[1]+1)
			except:
				ColorBelow = -1

			try:
				ColorRight = ip.getPixel(pix[0]+1,pix[1])
			except:
				ColorRight = -1

			# mimics 2D 4-neighbor erosion
			if thisColor != ColorLeft or thisColor != ColorAbove or thisColor != ColorBelow or thisColor != ColorRight:
				self.edgePixels.append([pix[0],pix[1]])

		# TODO: edgeSize has to be edgeLength !!! involve proper length measurement, see issue #1
		self.edgeSize = 0
		for pix in self.edgePixels:
			self.edgeSize += realSizes[pix[0]][pix[1]]

		# TODO: edgeSize has to be edgeLength !!! involve proper length measurement, see issue #1
		# lower value means higher circularity
		self.circularity = abs(self.area - ((self.edgeSize**2)/(4*math.pi)))/self.area


def main():
	# test that sizes of realSizes and imp matches
	checkSize2DarrayVsImgPlus(realSizes, imp);


	backgroundPixelValue = 1 # in case of cell nuclei
	if (not inputImageShowsNuclei):
		backgroundPixelValue = 2 # in case of cell membranes

	# fix pixel values;
	for x in range(imp.getWidth()):
		for y in range(imp.getHeight()):
			if (ip.getPixel(x, y) == backgroundPixelValue or ip.getPixel(x, y) == 0):
				ip.set(x,y,0)
			else:
				ip.set(x,y,255)

	#Detect Nuclei
	IJ.run(imp, "HMaxima local maximum detection (2D, 3D)", "minimum=1 threshold=0");
	labelMap = IJ.getImage()
	LPP = labelMap.getProcessor()
	labeledPixels = LPP.getPixels()

	#Detect all Pixel belonging to one Color
	# (builds a list of lists of pixel coords -- pixelPerColor[label][0] = first coordinate
	pixelPerColor = {}

	for x in range(labelMap.width):
		for y in range(labelMap.height):
			MyColor = LPP.getPixel(x,y)
			if  MyColor != 0:
				if str(MyColor) in pixelPerColor:
					pixelPerColor[str(MyColor)].append([x,y])
				else:
					pixelPerColor[str(MyColor)] = [[x,y]]

	# a list of nuclei objects
	nuclei = []

	for Color in pixelPerColor:
		nuclei.append(Nucleus(pixelPerColor[Color],Color))

	circularitySum = 0 
	sizesum = 0

	for nucl in nuclei:
		circularitySum += nucl.circularity
		sizesum += nucl.area

	print("Average Circularity: "+str(circularitySum/len(nuclei)))
	print("Average Area: "+str(sizesum/len(nuclei))+" square microns")

	print("Creating output image ...")
	OutputPixels = [[0 for y in range(imp.width)] for x in range(imp.height)]
	#
	# red nuclei   -- does not fit into circularity range
	# blue nuclei  -- does not fit into area range
	# white nuclei -- fit into both ranges
	for nucl in nuclei:
		if (filterCirc == True and nucl.circularity >= circularityMin and nucl.circularity <= circularityMax):
			for pix in nucl.Pixels:
				OutputPixels[pix[1]][pix[0]] = 0xFF0000
		elif (filterArea == True and nucl.area >= areaMin and nucl.area <= areaMax):
			for pix in nucl.Pixels:
				OutputPixels[pix[1]][pix[0]] = 0xFF
		else:
			for pix in nucl.Pixels:
				OutputPixels[pix[1]][pix[0]] = 0xFFFFFF

	OutputPixelsNew = reduce(lambda x,y :x+y ,OutputPixels)
	cp = ColorProcessor(labelMap.getWidth() ,labelMap.getHeight(), OutputPixelsNew)
	OutputImg = ImagePlus("OutputImg", cp)
	OutputImg.show()


	if (showRawData):
		# create an output table with three columns: label, circularity, area, size, positionX, positionY
		# 
		print("Populating a table...")
		rt = ResultsTable()
		for nucl in nuclei:
			rt.incrementCounter()
			rt.addValue("label"                            ,nucl.Color)
			rt.addValue("circularity (lower more roundish)",nucl.circularity)
			rt.addValue("area (um^2)"                      ,nucl.area)
			rt.addValue("area (px)"                        ,nucl.size)
			rt.addValue("centreX (px)"                     ,nucl.centreX)
			rt.addValue("centreY (px)"                     ,nucl.centreY)
		rt.show("Nuclei properties")


	print("Done.")


main()
