#@boolean (label="Input image shows nuclei (checked) or membranes (unchecked) ") inputImageShowsNuclei
#
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

#Get ROI
bigImg = IJ.getImage()
RoiD  = ij.ImagePlus.getRoi(bigImg)

realSizes = [[1 for y in range(bigImg.height)] for x in range(bigImg.width)]

RoiSize = 0
for point in RoiD:
	RoiSize += realSizes[point.x][point.y]

if RoiD != None:
	print RoiD
	
	noNumbers = False
	results = []
	densities = []
	numbers = []

	#Let the user choose an input folder
	dc1 = DirectoryChooser("Choose your input folder")
	InputFolder = dc1.getDirectory()

	if (InputFolder is None):
		sys.exit('User canceled Dialog!')

	for filename in os.listdir(InputFolder):
		imp = IJ.openImage(InputFolder+filename)

		if imp != None:
			ip = imp.getProcessor()

			backgroundPixelValue = 1 # in case of cell nuclei
			if (not inputImageShowsNuclei):
				backgroundPixelValue = 2 # in case of cell membranes
			# fix pixel values
			for x in range(0, imp.getWidth()):
				for y in range(0, imp.getHeight()):
					if (ip.getPixel(x, y) == backgroundPixelValue or ip.getPixel(x, y) == 0):
						ip.set(x,y,0)
					else:
						ip.set(x,y,255)
	
			# detect nuclei
			IJ.run(imp, "HMaxima local maximum detection (2D, 3D)", "minimum=1 threshold=0");
			labelMap = IJ.getImage()
			labelMapProcessor = labelMap.getProcessor()

			# Count number of different colors in label map = Count nuclei
			ColorsInRoi = set()
		
			for point in RoiD:
				ColorsInRoi.add(labelMapProcessor.getPixel(point.x,point.y))
	
			labelMap.close()
			numberOfNuclei = len(ColorsInRoi) - 1
			
			results.append((filename,numberOfNuclei))
			densities.append((float(numberOfNuclei)/float(RoiSize))*100)
	
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
	print('All files processed.')
		
else:
	print("Please select your area of interest before you run this script.")


