# THIS SCRIPT IS OLD AND NOT PROPERLY MAINTAINED YET!
#
#@boolean(label="Display horizontal change ", value=True) X_Change
#@boolean(label="Display vertical change", value = False) Y_Change
#@int(label="Accuracy (Number of points calculated to show the graph)", value="50") accuracy
#@int(label="Interval Size",value="50") intervalSize
#@boolean (label="Input image shows nuclei (checked) or membranes (unchecked) ") inputImageShowsNuclei
#@File (style="directory", label="Input directory") inputDir
#@File (style="directory", label="Output directory") outputDir

# This script displays the density differences in a given ROI over the X- or Y-Axis (or both)
# It takes a folder of images, where the density is visualized (The Output of neighborAnalysis.py)
# and creates text output, that can be visualized with ShowPlot.py,
# and one text-File with the information about the Roi.

# Usage:
# 	- Run Fiji
#	- Make sure that the update site SCF-MPI-CBG is activated
# 	- Open one of your images
# 	- Select the Area of Interest
#	- Run this script
#	- Choose the folder with all your input images
#	- Choose an output folder

from copy import copy
from ij import IJ
import ij.ImagePlus
from ij.gui import Roi
from ij.io import DirectoryChooser
import sys
import os
import struct
from ij.process import ImageConverter
from ij.gui import Plot

# this section adds a folder, in which this very script is living,
# to the current search paths so that we can import our "library script"
import sys.path
import os.path
import inspect
sys.path.append(os.path.dirname(inspect.getfile(inspect.currentframe())))

# import our "library script"
from realCoords import *

#Choose input folder and location of output folders
#dc1 = DirectoryChooser("Choose your input folder")
#InputFolder = dc1.getDirectory()

#dc2 = DirectoryChooser("Choose an output folder")
#OutputFolder = dc2.getDirectory()

InputFolder = inputDir.getAbsolutePath() + "/"
OutputFolder = outputDir.getAbsolutePath() + "/"

if (OutputFolder is None or InputFolder is None):
	sys.exit('User canceled Dialog!')

#Create Output folders
if X_Change:
	if not os.path.exists(OutputFolder+"Horizontal_Change"):
		os.mkdir(OutputFolder+"Horizontal_Change")
if Y_Change:
	if not os.path.exists(OutputFolder+"Vertical_Change"):
		os.mkdir(OutputFolder+"Vertical_Change")


bigImg = IJ.getImage()
RoiD  = ij.ImagePlus.getRoi(bigImg)
Bip = bigImg.getProcessor()

realSizes = [[1 for y in range(bigImg.height)] for x in range(bigImg.width)]

realCoordinates = [[[0.0,0.0] for y in range(bigImg.height)] for x in range(bigImg.width)]
for i in range(1, bigImg.width):
	realCoordinates[i][0] = [realCoordinates[i-1][0][0] + realSizes[i-1][0], 0.0]

for i in range(1, bigImg.height):
	realCoordinates[0][i] = [0.0, realCoordinates[0][i-1][1] + realSizes[0][i-1]]

for x in range (1, bigImg.width):
	for y in range (1, bigImg.height):
		realX = realCoordinates[x-1][y][0] + realSizes[x-1][y]
		realY = realCoordinates[x][y-1][1] + realSizes[x][y-1]
		realCoordinates[x][y] = [copy(realX), copy(realY)]

		
if RoiD != None:

	#Create a File with the Roi information, just in case the user forgets to write it down.
	SaveFile = open(OutputFolder+'Roi.txt','w')
	SaveFile.write(str(RoiD))
	SaveFile.close()

	#Find the Edge of the Roi
	
	xmin = float("inf")
	xmax = 0
	ymin = float("inf")
	ymax = 0
	
	for pix in RoiD:
		realX = realCoordinates[pix.x][pix.y][0]
		realY = realCoordinates[pix.x][pix.y][1]
		if realX < xmin:
			xmin = realX
		elif realX > xmax:
			xmax = realX
		if realY < ymin:
			ymin = realY
		elif realY > ymax:
			ymax = realY

	
	for filename in os.listdir(InputFolder):

		imp = IJ.openImage(InputFolder+filename)
		
		if imp is not None:
			converter = ImageConverter(imp)
			converter.convertToGray8()
		
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
	
			
			#Detect nuclei
			IJ.run(imp, "HMaxima local maximum detection (2D, 3D)", "minimum=1 threshold=0");
			labelMap = IJ.getImage()
			labelMapProcessor = labelMap.getProcessor()
			
			ColorAndPixels = {}

			#Find all Pixels per Color (for detecting the nuclei centers later)
			for point in RoiD:
				MyColor = labelMapProcessor.getPixel(point.x,point.y)
				if MyColor != 0:
					if  MyColor in ColorAndPixels:
						ColorAndPixels[MyColor].append([point.x,point.y])
					else:
						ColorAndPixels[MyColor] = [[point.x,point.y]]

			NucleiCenters = {}
			NucleiDensities = {}
			
			#Detect centers of all nuclei inside ROI (by computing the average values of the containing pixels)
			for Color in ColorAndPixels:
				Pixels = ColorAndPixels[Color]
				sumX = 0
				sumY = 0
				for pix in Pixels:
					sumX += realCoordinates[pix[0]][pix[1]][0]
					sumY += realCoordinates[pix[0]][pix[1]][1]
				densColor = ip.getPixel(Pixels[0][0],Pixels[0][1])

				NucleiCenters[Color] = ((sumX/len(Pixels)),(sumY/len(Pixels)))
				NucleiDensities[Color] = densColor
			
			if X_Change:

				#Calculate the Graph Points
				GraphPoints = []
				if round((xmax-xmin)/accuracy) == 0:
					print("The accuracy is too high for this ROI (Horizontal)")
				for i in range(int(xmin),int(xmax),int(round((xmax-xmin)/accuracy))):
					intervalStart = i - intervalSize / 2
					intervalEnd = i + intervalSize / 2

					#Calculate the average density of the region
					densitySum = 0
					numberOfNuclei = 0
					for Color in NucleiCenters:
						nucl = NucleiCenters[Color]
						if nucl[0] >= intervalStart and nucl[0] < intervalEnd:
							densitySum += NucleiDensities[Color]
							numberOfNuclei += 1
		
					if numberOfNuclei != 0:
						averageDensity = float(numberOfNuclei)
						
						GraphPoints.append((i,averageDensity))


				plotX = []
				plotY = []
				for point in GraphPoints:
					plotX.append(point[0])
					plotY.append(point[1])

				plot = Plot("Cell count in vertical blocks", "Horizontal position", "Number of cells per block", plotX, plotY)
				plot.show();

				plotImp = IJ.getImage()
				IJ.saveAs(plotImp, "Tiff", OutputFolder+'Horizontal_Change/'+filename+'.plot.tif');
				
				# Create the output text file
				SaveFile = open(OutputFolder+'Horizontal_Change/'+filename+'.txt','w')
				
				for point in GraphPoints:
					SaveFile.write(str(point[0])+" "+str(point[1])+"\n")
				
				SaveFile.close()
		
			if Y_Change:

				#Calculate the Graph Points
				GraphPoints = []
				if round((ymax-ymin)/accuracy) == 0:
					print("The accuracy is too high for this ROI (Vertical)")
				for i in range(int(ymin),int(ymax),int(round((ymax-ymin)/accuracy))):
					intervalStart = i - intervalSize / 2
					intervalEnd = i + intervalSize / 2

					#Calculate the average density of the region
					densitySum = 0
					numberOfNuclei = 0
					for Color in NucleiCenters:
						nucl = NucleiCenters[Color]
						if nucl[1] >= intervalStart and nucl[1] < intervalEnd:
							densitySum += NucleiDensities[Color]
							numberOfNuclei += 1
		
					if numberOfNuclei != 0:
						averageDensity = float(numberOfNuclei)
						
						GraphPoints.append((i,averageDensity))

				plotX = []
				plotY = []
				for point in GraphPoints:
					plotX.append(point[0])
					plotY.append(point[1])

				plot = Plot("Cell count in horizontal blocks", "Vertical position", "Number of cells per block", plotX, plotY)
				plot.show();

				plotImp = IJ.getImage()
				IJ.saveAs(plotImp, "Tiff", OutputFolder+'Vertical_Change/'+filename+'.plot.tif');
				
				
				Create the output text file
				SaveFile = open(OutputFolder+'Vertical_Change/'+filename+'.txt','w')
				
				for point in GraphPoints:
					SaveFile.write(str(point[0])+" "+str(point[1])+"\n")
				
				SaveFile.close()			
	
			print('Image "'+filename+'" successfully processed')
			labelMap.close()

		else:
			print("Ignoring "+filename)

	print
	print("All files processed.")
		
else:
	print("Please select the ROI before you run this script")
	
