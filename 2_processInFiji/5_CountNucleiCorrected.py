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
#@File (style="directory", label="Input directory") inputDir

# This script counts the nuclei in a given ROI over time.
# It takes a folder of binary images and the ROI as input, and then displays a table
# in which the number of nuclei for each timestamp is saved.

# Usage:
# 	- Run Fiji
#	- Make sure that the update site SCF-MPI-CBG is activated
# 	- Open one of your images
# 	- Select the Area of Interest
#	- Run this script
#	- Choose the folder with all your input images


from ij import IJ
import ij.ImagePlus
from ij.gui import Roi
from ij.io import DirectoryChooser
from ij.measure import ResultsTable
import os
import sys

# this section adds a folder, in which this very script is living,
# to the current search paths so that we can import our "library script"
import sys.path
import os.path
import inspect
sys.path.append(os.path.dirname(inspect.getfile(inspect.currentframe()))+"/lib")

# import our "library script"
from importsFromImSAnE import *

# import the same Nucleus class to make sure the very same calculations are used
from Nucleus import Nucleus
from chooseNuclei import *

#Get ROI
bigImg = IJ.getImage()
RoiD  = ij.ImagePlus.getRoi(bigImg)

if RoiD != None:
	print RoiD

	# reads the area_per_pixel information, already in squared microns
	realSizes = readRealSizes(aMapFile.getAbsolutePath());

	# read the 'real Coordinates', that take into account the different pixel sizes
	realCoordinates = readRealCoords(xMapFile.getAbsolutePath(),yMapFile.getAbsolutePath(),zMapFile.getAbsolutePath())

	# test that sizes of realSizes and bigImg matches
	checkSize2DarrayVsImgPlus(realSizes, bigImg);
	checkSize2DarrayVsImgPlus(realCoordinates, bigImg)

	# determine the proper area of the reference ROI
	RoiSize = 0.0
	for point in RoiD:
		RoiSize += realSizes[point.x][point.y]

	#dc1 = DirectoryChooser("Choose your input folder")
	#InputFolder = dc1.getDirectory()
	InputFolder = inputDir.getAbsolutePath() + "/"

	if (InputFolder is None):
		sys.exit('User canceled Dialog!')

	results = []
	densities = []
	numbers = []
	noNumbers = False

	for filename in os.listdir(InputFolder):
		imp = IJ.openImage(InputFolder+filename)

		if imp != None:
			# test that sizes of realSizes and imp matches
			checkSize2DarrayVsImgPlus(realSizes, imp);
			checkSize2DarrayVsImgPlus(realCoordinates, imp)

			backgroundPixelValue = 1 # in case of cell nuclei
			if (not inputImageShowsNuclei):
				backgroundPixelValue = 2 # in case of cell membranes

			# obtain list of viable nuclei
			nuclei = chooseNuclei(imp,backgroundPixelValue,realSizes,realCoordinates, filterArea,areaMin,areaMax, filterCirc,circularityMin,circularityMax)
			width  = imp.getWidth()
			height = imp.getHeight()
			imp.close()

			# ------- analysis starts here -------
			# Count number of nuclei inside the ROI (is inside whenever only single pixel is inside the ROI),
			# to optimize for speed, we render all valid nuclei and detect which nuclei are touching the ROI

			# assign a unique integer value to every nuclei
			for i in range(len(nuclei)):
				nuclei[i].DrawValue = i+1

			# render the nuclei (NB: will be of the right size, ROI coords will be compatible)
			drawChosenNucleiValue(width,height, nuclei)
			imp = IJ.getImage()
			ip = imp.getProcessor()

			# sweep the ROI to see which nuclei are touching it
			colorsInROI = set()
			for point in RoiD:
				val = ip.getf(point.x,point.y)
				# add only non-background voxels
				if val > 0:
					colorsInROI.add(val)

			numberOfNuclei = len(colorsInROI)
			imp.close()

			# ------- reporting starts here -------
			#Extract number from filename if existing (for the sorting afterwards)
			number = ''
			for c in filename:
				if c == '0' or c == '1' or c == '2' or c == '3' or c == '4' or c == '5' or c == '6' or c == '7' or c == '8' or c == '9': 
					number += c
	
			if not noNumbers:
				if number == '':
					noNumbers = True
				else:
					number = int(number)
					numbers.append(number)

			results.append((filename,numberOfNuclei))
			densities.append(float(numberOfNuclei)/float(RoiSize))

			print('Successfully processed "'+ filename+'"')

		else:
			print("Ignoring '"+filename+"'")

		
	# Create Results table
	table = ResultsTable()

	# Add the selected Roi to the table (Just if the user forgets)
	table.incrementCounter()
	table.addValue('Image',str(RoiD))

	# Add values to the table
	if noNumbers:
		for i in range(len(results)):
			table.incrementCounter()
			table.addValue('Image',results[i][0])
			table.addValue('Number of Nuclei',results[i][1])
			table.addValue('Density', densities[i])
	else:
		for i in range(len(results)):
			table.incrementCounter()
			table.addValue('Image',results[i][0])
			table.addValue('Extracted Number',numbers[i])
			table.addValue('Number of Nuclei',results[i][1])
			table.addValue('Density', densities[i])

	table.show('Results')
	IJ.saveAs("Results", InputFolder+"/nucleiList.xls")
	IJ.saveAs("Results", InputFolder+"/nucleiList.txt")
	IJ.saveAs("Results", InputFolder+"/nucleiList.csv")

	print
	print('All files processed.')

else:
	print("Please select your area of interest before you run this script.")


