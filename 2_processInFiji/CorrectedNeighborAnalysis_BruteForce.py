#@int (label="Search radius [microns]:", value=50) R
#@boolean (label="Input image shows nuclei (checked) or membranes (unchecked) ") inputImageShowsNuclei
#@File (label="X coordinate map:") xMapFile
#@File (label="Y coordinate map:") yMapFile
#@File (label="Z coordinate map:") zMapFile
#@File (style="directory", label="Input directory") inputDir
#@File (style="directory", label="Output directory") outputDir

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
sys.path.append(os.path.dirname(inspect.getfile(inspect.currentframe())))

# import our "library script"
from importsFromImSAnE import *


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
if not os.path.exists(OutputFolder+"OutputTables"):
	os.mkdir(OutputFolder+"OutputTables")

FirstImage = None
for filename in os.listdir(InputFolder):
	FirstImage = IJ.openImage(InputFolder+filename)
	if FirstImage != None:
		break

if FirstImage == None:
	sys.exit('No images in input folder ' + InputFolder + '!')


#Calculate the 'real Coordinates', that take into account the different pixel sizes
realCoordinates = readRealCoords(xMapFile.getAbsolutePath(),yMapFile.getAbsolutePath(),zMapFile.getAbsolutePath());

# Process the images
for filename in os.listdir(InputFolder):

	imp = IJ.openImage(InputFolder+filename)

	if imp is not None:
		ip = imp.getProcessor()	

		backgroundPixelValue = 1 # in case of cell nuclei
		if (not inputImageShowsNuclei):
			backgroundPixelValue = 2 # in case of cell membranes
		
		# fix pixel values;
		for x in range(imp.width):
			for y in range(imp.height):
				if (ip.getPixel(x, y) == backgroundPixelValue or ip.getPixel(x, y) == 0):
					ip.set(x,y,0)
				else:
					ip.set(x,y,255)

		#Detect nuclei
		print("Detecting nuclei...")			
		
		IJ.run(imp, "HMaxima local maximum detection (2D, 3D)", "minimum=1 threshold=0")
		labelMap = IJ.getImage()
		labelMapProcessor = labelMap.getProcessor()

		print("Calculating the nuclei centers...")
		
		ColorAndPixels = {}
					
		#Find all Pixels per Color (for detecting the nuclei centers later)
		for x in range(imp.width):
			for y in range(imp.height):
				MyColor = labelMapProcessor.getPixel(x,y)
				if MyColor != 0:
					if  MyColor in ColorAndPixels:
						ColorAndPixels[MyColor].append([x,y])
					else:
						ColorAndPixels[MyColor] = [[x,y]]
					
		NucleiCenters = {}
					
		#Detect centers of all nuclei inside ROI (by computing the average values of the containing pixels)
		for Color in ColorAndPixels:
			Pixels = ColorAndPixels[Color]
			sumX = 0
			sumY = 0
			sumZ = 0
			for pix in Pixels:
				sumX += realCoordinates[pix[0]][pix[1]][0]
				sumY += realCoordinates[pix[0]][pix[1]][1]
				sumZ += realCoordinates[pix[0]][pix[1]][2]
		
			# the real (in micron units) 3D coordinate of nuclei centre
			NucleiCenters[Color] = [sumX/len(Pixels),sumY/len(Pixels),sumZ/len(Pixels)]


		#Count the neighbors of each nucleus 
		print("Counting the neighbors...")
		
		neighbors = {}
		
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

		#Creating the output image
		print("Creating output image...")
		
		maxim2 = 1
		#NB: zero would make more sense but it is prone to division-by-zero
		
		for Color in neighbors:
			if neighbors[Color] > maxim2:
				maxim2 = neighbors[Color]	
		
		OutputPixels = []
		
		for y in range(imp.height):
			for x in range(imp.width):
				Color = labelMapProcessor.getPixel(x,y)
				if Color == 0:
					OutputPixels.append(0)
				else:
					OutputPixels.append((float(neighbors[Color])/float(maxim2))*255)
					
		labelMap.close()
		
		fp = FloatProcessor(imp.width, imp.height, OutputPixels, None)  
		OutputImg = ImagePlus("OutputImg", fp)
		
		fs = FileSaver(OutputImg)
		fs.saveAsTiff(OutputFolder+"CountNeighborsWithinRadius"+str(R)+'/'+filename)
		
		#Create output table
		print("Creating output table...")

		table = ResultsTable()

		# Add values to the table
		for Color in neighbors:
			table.incrementCounter()
			table.addValue('Center of nucleus', str(round(NucleiCenters[Color][0],2))+", "+str(round(NucleiCenters[Color][1],2))+", "+str(round(NucleiCenters[Color][2],2)))
			table.addValue('Number of neighbors within radius '+str(R),neighbors[Color])

		table.show('Results')
		IJ.saveAs("Results", OutputFolder+"OutputTables/"+filename+".xls")
		tablWindow = ij.WindowManager.getWindow("Results")
		tablWindow.close()
				
		print('Image "'+filename+'" successfully processed.')

	else:
		print("Ignoring " + filename)

print
print("All files processed.")

