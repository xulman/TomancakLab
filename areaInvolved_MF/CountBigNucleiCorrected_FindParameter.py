#@int(label="A big nucleus is everything bigger than ... Pixels", value=100) bigBorder
#@float(label="A nucleus has a maximum circularity of... (lower value means higher circularity)", value=0.5) maxCircularity
#@boolean (label="Input image shows nuclei (checked) or membranes (unchecked) ") inputImageShowsNuclei

# This script should be used to find siutable parameters for CountBigNuclei.py
# You'll see in blue the nuclei that are too small to be called 'big'
# And in red the ones that are not circular enough.

# Usage:
#	- Run Fiji
# 	- Make sure that the update site SCF-MPI-CBG is activated
#	- Open one representative image of your data
#	- Run this script
# 	- If you are not confident with the output, repeat with other parameters.

from ij import IJ
from ij import ImagePlus
import math
from ij.io import DirectoryChooser 
from ij.process import ColorProcessor 

# sys.path.append(os.path.abspath("/Users/ulman/p_Akanksha/git_repo/areaInvolved_MF"))
# from realAreas import *
execfile("/Users/ulman/p_Akanksha/git_repo/areaInvolved_MF/realAreas.py")

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


imp = IJ.getImage()
ip = imp.getProcessor()

# reads the area_per_pixel information, already in squared microns
realSizes = readRealSizes();

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

circularitySum = 0 
sizesum = 0

for nucl in nuclei:
	circularitySum += nucl.circularity
	sizesum += nucl.size

print("Average Circularity: "+str(circularitySum/len(nuclei)))
print("Average Size: "+str(sizesum/len(nuclei))+" Pixels")

print("Creating output image ...")

OutputPixels = [[0 for y in range(imp.width)] for x in range(imp.height)]

for nucl in nuclei:
	if nucl.circularity > maxCircularity:
		for pix in nucl.Pixels:
			OutputPixels[pix[1]][pix[0]] = 0xFF0000
	elif nucl.size <= bigBorder:
		for pix in nucl.Pixels:
			OutputPixels[pix[1]][pix[0]] = 0xFF
	else:
		for pix in nucl.Pixels:
			OutputPixels[pix[1]][pix[0]] = 0xFFFFFF

OutputPixelsNew = reduce(lambda x,y :x+y ,OutputPixels)

cp = ColorProcessor(labelMap.getWidth() ,labelMap.getHeight(), OutputPixelsNew)  
OutputImg = ImagePlus("OutputImg", cp)

OutputImg.show()

print("Done.")

			

