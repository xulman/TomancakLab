#@int(label="A big nucleus is everything bigger than ... um^2", value=100) bigBorder
#@float(label="A nucleus has a maximum circularity of... (lower value means higher circularity)", value=0.5) maxCircularity
#@boolean (label="Input image shows nuclei (checked) or membranes (unchecked) ") inputImageShowsNuclei
#@File (label="Pixel areas map:") aMapFile
#@File (style="directory", label="Input directory") inputDir

# This script counts all the nuclei, that are nearly circular and bigger than a given threshold.
# It takes a folder of segmented binary images and outputs a table with the number of big nuclei per timestamp.

# Usage:
# 	- Find suitable parameters with CountBigNuclei_FindParameter.py
#	- Run Fiji
# 	- Make sure that the update site SCF-MPI-CBG is activated
#	- Run this script
# 	- Choose an input folder
# 	- You'll get a table out of it, that you can visualize or measure it with an table calculating program like Excel.

from ij import IJ
import math
from ij.io import DirectoryChooser 
import os
import sys
from ij.measure import ResultsTable

# this section adds a folder, in which this very script is living,
# to the current search paths so that we can import our "library script"
import sys.path
import os.path
import inspect
sys.path.append(os.path.dirname(inspect.getfile(inspect.currentframe())))

# import our "library script"
from importsFromImSAnE import *

class Nucleus:

	def __init__(self,Pixels,Color):
		self.Pixels = Pixels
		self.Color = Color
		self.size = 0
		for pix in Pixels:
			self.size += realSizes[pix[0]][pix[1]]
			
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
			
			if thisColor != ColorLeft or thisColor != ColorAbove or thisColor != ColorBelow or thisColor != ColorRight:
				self.edgePixels.append([pix[0],pix[1]])
		
		self.edgeSize = 0
		for pix in self.edgePixels:
			self.edgeSize += realSizes[pix[0]][pix[1]]


		self.circularity = abs(self.size - ((self.edgeSize**2)/(4*math.pi)))/self.size # lower value means higher circulatriy


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
		ip = imp.getProcessor()

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
		pixelPerColor = {}
		
		for x in range(labelMap.width):
			for y in range(labelMap.height):
				MyColor = LPP.getPixel(x,y)
				if  MyColor != 0:
					if str(MyColor) in pixelPerColor:
						pixelPerColor[str(MyColor)].append([x,y])
					else:
						pixelPerColor[str(MyColor)] = [[x,y]]
		
		nuclei = []
		
		for Color in pixelPerColor:
			nuclei.append(Nucleus(pixelPerColor[Color],Color))
		
		bigNuclei = 0
		
		for nucl in nuclei:
			if nucl.circularity < maxCircularity and nucl.size > bigBorder:
				bigNuclei += 1
	
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
	
		labelMap.close()
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

print
print("All files processed.")
