#@int (label="Search radius:", value=50) R
#@boolean (label="Input image shows nuclei (checked) or membranes (unchecked) ") inputImageShowsNuclei
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

#Function that helps sorting Pixels
def PixelKey(pix):
	return (pix[0]*100000 + pix[1])

#Gives the box for specific coordinates
def GiveBox(pix):
	return [int(round(1000/maxim[0] * pix[0])),int(round(1000/maxim[1] * pix[1]))]

#Returns all boxes that are partly or fully inside the search radius
def BoxesInside(center):
	global CirclePixels2D
	
	BoxesInside = set()
	for l in CirclePixels2D:
		line = CirclePixels2D[l]
		EndRight = line[-1][1] + center[1]
		EndLeft = line[0][1] + center[1]
		x = line[0][0] + center[0]
		startBox = GiveBox([x,EndLeft])
		endBox = GiveBox([x,EndRight])

		for ybox in range(startBox[1],endBox[1]):
			BoxesInside.add((startBox[0],ybox))

	return BoxesInside		



#Choose input folder and location of output folders

#dc1 = DirectoryChooser("Choose your input folder")
#InputFolder = dc1.getDirectory()

#dc2 = DirectoryChooser("Choose an output folder")
#OutputFolder = dc2.getDirectory()

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
	
realSizes = [[float(randint(1,3)) for y in range(FirstImage.height)] for x in range(FirstImage.width)]


#Create a Circle

CirclePixels = set()

x = 0
y = R
F = 1 - R   
CirclePixels.add((0,R))
CirclePixels.add((R,0))
CirclePixels.add((0,-R))
CirclePixels.add((-R,0))
   
while (x < y):  
	if (F < 0) : 
		F = F + 2*x + 1   
		x = x + 1   
	else :
		F = F + 2*x - 2*y + 2   
		x = x + 1   
		y = y - 1   
   
	CirclePixels.add((x,y))
	CirclePixels.add((y,x))   
	CirclePixels.add((-x,y))
	CirclePixels.add((y,-x))   
	CirclePixels.add((x,-y))
	CirclePixels.add((-y,x))   
	CirclePixels.add((-x,-y))
	CirclePixels.add((-y,-x))

CirclePixelsSorted = sorted(CirclePixels, key = PixelKey)


#Make an dict with the circle pixels per line

CirclePixels2D = {}

ActualColumn = -R
ActualColumnPixels = []

for pix in CirclePixelsSorted:
	if pix[0] == ActualColumn:
		ActualColumnPixels.append([pix[0],pix[1]])
	else:
		CirclePixels2D[ActualColumn] = deepcopy(ActualColumnPixels)
		ActualColumnPixels = [[pix[0],pix[1]]]
		ActualColumn = pix[0]

CirclePixels2D[ActualColumn] = deepcopy(ActualColumnPixels)	

#Calculate the 'real Coordinates', that take into account the different pixel sizes

realCoordinates = [[[0.0,0.0] for y in range(FirstImage.height)] for x in range(FirstImage.width)]
for i in range(1, FirstImage.width):
	realCoordinates[i][0] = [realCoordinates[i-1][0][0] + realSizes[i-1][0], 0.0]

for i in range(1, FirstImage.height):
	realCoordinates[0][i] = [0.0, realCoordinates[0][i-1][1] + realSizes[0][i-1]]

for x in range (1, FirstImage.width):
	for y in range (1, FirstImage.height):
		realX = realCoordinates[x-1][y][0] + realSizes[x-1][y]
		realY = realCoordinates[x][y-1][1] + realSizes[x][y-1]
		realCoordinates[x][y] = [copy(realX), copy(realY)]
    

maxim = [floor(realCoordinates[FirstImage.width-1][FirstImage.height-1][0]),floor(realCoordinates[FirstImage.width-1][FirstImage.height-1][1])]

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
			for pix in Pixels:
				sumX += realCoordinates[pix[0]][pix[1]][0]
				sumY += realCoordinates[pix[0]][pix[1]][1]
		
					
			NucleiCenters[Color] = [sumX/len(Pixels),sumY/len(Pixels)]

		# Later, we will just have to search for neighbors in the boxes that are partly or fully inside the search radius,
		# and not in the whole image. 
		
		print("Putting the nuclei in boxes ...")
		
		boxes = [ [ []for y in range(0,int(maxim[1]),int(maxim[1]/1000))] for x in range(0,int(maxim[0]),int(maxim[0]/1000))]
		
		
		for Color in NucleiCenters:
			center = NucleiCenters[Color]
			box = GiveBox(center)
			boxes[box[0]][box[1]].append(Color)

		#Count the neighbors of each nucleus 
		print("Counting the neighbors...")
		
		neighbors = {}
		
		for Color in NucleiCenters:
			center = NucleiCenters[Color]
			boxesInside = BoxesInside(center)
			numberOfNeighbors = 0
			for box in boxesInside:
				for Nucl in boxes[box[0]][box[1]]:
					# test if this nucleus is inside the search radius
					OtherCenter = NucleiCenters[Nucl]
					distanceSquared = (OtherCenter[0] - center[0])**2 + (OtherCenter[1] - center[1])**2
					if distanceSquared < R**2:
						numberOfNeighbors +=1
					
			neighbors[Color] = numberOfNeighbors-1

		#Creating the output image
		print("Creating output image...")
		
		maxim2 = 0
		
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
			table.addValue('Center of nucleus', str(round(NucleiCenters[Color][0],2))+", "+str(round(NucleiCenters[Color][1],2)))
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
	
