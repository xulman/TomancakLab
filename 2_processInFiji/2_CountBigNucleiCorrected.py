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
#@File (style="directory", label="Input directory") inputDir

# This script counts all the nuclei, that are nearly circular and their areas are within the given interval.
# It takes a folder of segmented binary images and outputs a table with the number of big nuclei per timestamp.

# Usage:
# 	- Find suitable parameters with CountBigNucleiCorrected_FindParameter.py
#	- Run Fiji
# 	- Make sure that the update site SCF-MPI-CBG is activated
#	- Run this script
# 	- Choose an input folder
# 	- You'll get a table out of it, that you can visualize or measure it with an table calculating program like Excel.

from ij import IJ
from ij.io import DirectoryChooser 
import os
import sys
from ij.measure import ResultsTable

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


# reads the area_per_pixel information, already in squared microns
realSizes = readRealSizes(aMapFile.getAbsolutePath());

#Choose input folder

#dc1 = DirectoryChooser("Choose your input folder")
#InputFolder = dc1.getDirectory()
InputFolder = inputDir.getAbsolutePath() + "/"

if (InputFolder is None):
		sys.exit('User canceled Dialog!')

BigNucleiPerTimestamp = []
Images = []
numbers = []
noNumbers = False

for filename in os.listdir(InputFolder):
	imp = IJ.openImage(InputFolder+filename)
	
	if imp != None:
		# test that sizes of realSizes and imp matches
		checkSize2DarrayVsImgPlus(realSizes, imp);
		
		backgroundPixelValue = 1 # in case of cell nuclei
		if (not inputImageShowsNuclei):
			backgroundPixelValue = 2 # in case of cell membranes

		# obtain list of viable nuclei
		nuclei = chooseNuclei(imp,backgroundPixelValue,realSizes, filterArea,areaMin,areaMax, filterCirc,circularityMin,circularityMax);

		# ------- analysis starts here -------
		bigNuclei = len(nuclei)

#		for nucl in nuclei:
#			if nucl.doesQualify(filterArea,areaMin,areaMax, filterCirc,circularityMin,circularityMax) == True:
#				bigNuclei += 1
#NB: every nuclei in the list qualifies...

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
	
		Images.append(filename)
		BigNucleiPerTimestamp.append(bigNuclei)
	
		imp.close()
	
		print("Image "+filename+" successfully processed.")

	else:
		print("Ignoring "+filename)
	

# Create Results table
	
table = ResultsTable()

# Add values to the table
if noNumbers:
	for i in range(len(BigNucleiPerTimestamp)):
		table.incrementCounter()
		table.addValue('Image', Images[i])
		table.addValue('Number of big Nuclei',BigNucleiPerTimestamp[i])
else:
	for i in range(len(BigNucleiPerTimestamp)):
		table.incrementCounter()
		table.addValue('Image', Images[i])
		table.addValue('Extracted Number',numbers[i])
		table.addValue('Number of big Nuclei',BigNucleiPerTimestamp[i])

table.show('Results')
IJ.saveAs("Results", inputDir+"/nucleiList.xls")
IJ.saveAs("Results", inputDir+"/nucleiList.txt")
IJ.saveAs("Results", inputDir+"/nucleiList.csv")

print
print("All files processed.")
