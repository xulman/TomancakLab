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
#@int (label="Search radius [microns]:", value=50) R
#@File (style="directory", label="Input directory") inputDir
#@File (style="directory", label="Output directory") outputDir
#@int (label="Vizu: estimated max no. of nuclei [-1 for perFrame autodetection; 255 to defacto disable it]:", value=30) maxim1

#This script takes a folder of segmented binary images and measures properties of neighboring objects. 
#The Output images are stored in two folders: One contains the results of counting the neighbors in a firm radius,
#in the second one, you'll find the output tables. 
#In the output images, cells with many neighbors are brighter than cells with few neighbors.

# Usage:
#	- Run Fiji
#	- Make sure that the update site SCF-MPI-CBG is activated
#	- Run this script
#	- Choose an input folder
#	- Choose an output folder

# make sure there is a "recognized" number used (and we don't like maxim1 = 0)
if maxim1 < 1:
	maxim1 = -1

import sys
import os
import ij.WindowManager
from copy import deepcopy,copy
from ij import IJ, ImagePlus
from random import randint
from math import floor
from ij.process import FloatProcessor
from ij.io import DirectoryChooser, FileSaver
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
from chooseNuclei import *


InputFolder = inputDir.getAbsolutePath() + "/"
OutputFolder = outputDir.getAbsolutePath() + "/"

if (InputFolder is None) or (OutputFolder is None):
	sys.exit('User canceled Dialog!')
	
print('Input folder: '+InputFolder)
print('Output folder: '+OutputFolder)

print('Initializing...')

#Create Output folders
if not os.path.exists(OutputFolder+"CountNeighborsWithinRadius"+str(R)):
	os.mkdir(OutputFolder+"CountNeighborsWithinRadius"+str(R))
if not os.path.exists(OutputFolder+"OutputTables"+str(R)):
	os.mkdir(OutputFolder+"OutputTables"+str(R))

FirstImage = None
for filename in os.listdir(InputFolder):
	FirstImage = IJ.openImage(InputFolder+filename)
	if FirstImage != None:
		break

if FirstImage == None:
	sys.exit('No images in input folder ' + InputFolder + '!')


# reads the area_per_pixel information, already in squared microns
realSizes = readRealSizes(aMapFile.getAbsolutePath());

#Calculate the 'real Coordinates', that take into account the different pixel sizes
realCoordinates = readRealCoords(xMapFile.getAbsolutePath(),yMapFile.getAbsolutePath(),zMapFile.getAbsolutePath());

# test that sizes of realSizes and bigImg matches
checkSize2DarrayVsImgPlus(realSizes, FirstImage);
checkSize2DarrayVsImgPlus(realCoordinates, FirstImage)

# Process the images
for filename in os.listdir(InputFolder):
	imp = IJ.openImage(InputFolder+filename)

	if imp is not None:
		# test that sizes of realSizes and imp matches
		checkSize2DarrayVsImgPlus(realSizes, imp);
		checkSize2DarrayVsImgPlus(realCoordinates, imp)

		backgroundPixelValue = 1 # in case of cell nuclei
		if (not inputImageShowsNuclei):
			backgroundPixelValue = 2 # in case of cell membranes

		# obtain list of viable nuclei
		nuclei = chooseNuclei(imp,backgroundPixelValue,realSizes,realCoordinates, filterArea,areaMin,areaMax, filterCirc,circularityMin,circularityMax)

		# ------- analysis starts here -------
		#Detect centers of all nuclei inside ROI (by computing the average values of the containing pixels)
		NucleiCenters = {}
		for nucl in nuclei:
			Pixels = nucl.Pixels;
			sumX = 0
			sumY = 0
			sumZ = 0
			for pix in Pixels:
				sumX += realCoordinates[pix[0]][pix[1]][0]
				sumY += realCoordinates[pix[0]][pix[1]][1]
				sumZ += realCoordinates[pix[0]][pix[1]][2]
		
			# the real (in micron units) 3D coordinate of nuclei centre
			NucleiCenters[nucl.Color] = [sumX/len(Pixels),sumY/len(Pixels),sumZ/len(Pixels)]

		#Count the neighbors of each nucleus 
		neighbors = {}
		maxim2 = 1
		#NB: zero would make more sense but it is prone to division-by-zero
		
		for Color in NucleiCenters:
			MyCenter = NucleiCenters[Color]
			numberOfNeighbors = 0
			for Nucl in NucleiCenters:
				# test if this nucleus is inside the search radius
				OtherCenter = NucleiCenters[Nucl]
				distanceSquared = (OtherCenter[0] - MyCenter[0])**2 + (OtherCenter[1] - MyCenter[1])**2 + (OtherCenter[2] - MyCenter[2])**2
				if distanceSquared < R**2:
					numberOfNeighbors +=1
					
			neighbors[Color] = numberOfNeighbors-1
			if neighbors[Color] > maxim2:
				maxim2 = neighbors[Color]

		# ------- reporting starts here -------
		#Creating the output image
		print("Creating output image...")

		if maxim1 == -1:
			maxim1 = maxim2;
		
		OutputPixels = [[0.0 for y in range(imp.width)] for x in range(imp.height)]
		for nucl in nuclei:
			nn = neighbors[nucl.Color]
			if nn > maxim1:
				nn = maxim1
			intensityColor = 255.0*float(nn)/float(maxim1)
			for pix in nucl.Pixels:
				OutputPixels[pix[1]][pix[0]] = intensityColor
		
		OutputPixelsNew = reduce(lambda x,y :x+y ,OutputPixels)
		fp = FloatProcessor(imp.width, imp.height, OutputPixelsNew, None)
		OutputImg = ImagePlus("Nuclei_Density_in_R="+str(R)+"_microns", fp)
		
		fs = FileSaver(OutputImg)
		fs.saveAsTiff(OutputFolder+"CountNeighborsWithinRadius"+str(R)+'/'+filename)
		
		#Create output table
		table = ResultsTable()

		# Add values to the table
		for Color in neighbors:
			table.incrementCounter()
			table.addValue('Center of nucleus', str(round(NucleiCenters[Color][0],2))+", "+str(round(NucleiCenters[Color][1],2))+", "+str(round(NucleiCenters[Color][2],2)))
			table.addValue('Number of neighbors within radius '+str(R),neighbors[Color])

		table.show('Results')
		IJ.saveAs("Results", OutputFolder+"OutputTables"+str(R)+"/"+filename+".xls")
		IJ.saveAs("Results", OutputFolder+"OutputTables"+str(R)+"/"+filename+".txt")
		IJ.saveAs("Results", OutputFolder+"OutputTables"+str(R)+"/"+filename+".csv")
		tablWindow = ij.WindowManager.getWindow("Results")
		tablWindow.close()
				
		# this forces to close the image even when it was modified
		IJ.run("Close")
		#imp.close()
		print('Successfully processed "'+ filename+'"')

	else:
		print("Ignoring " + filename)

print
print("All files processed.")

