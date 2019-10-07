#@ImagePlus (label="Image to back-projected:") inImp
#@File (label="X coordinate map:") xMapFile
#@File (label="Y coordinate map:") yMapFile
#@File (label="Z coordinate map:") zMapFile
#@float (label="Pixel size (microns per 1px):") pxSize
#@float (label="Downscale factor:") dsRatio

#@int   (label="Thickness of the outer main (image) layer (pixels):", min="1", description="The thicker it is, the less the rendering would \"see through it\".") pxThickness
#@int   (label="Thickness of the inner extra (blocking) layer (pixels):", min="0", description="Set to 0 to avoid creating this blocking inner layer.") pxExtraThickness
#@float (label="Value to draw with the extra layer:", description="This value is not considered if the above is set to 0. To make it practically invisible, set this to some small number.") valExtraThickness

# This script creates a 3D image that displays the original image before
# it got wrapped/embedded into the input inImp 2D image.
# The input image can be any scalar voxel type, does NOT work for RGB well.

from ij import IJ
import ij.ImagePlus
import ij.ImageStack
from ij.process import FloatProcessor
import math
import os
import sys

# this section adds a folder, in which this very script is living,
# to the current search paths so that we can import our "library script"
import sys.path
import os.path
import inspect
ScriptsRoot = os.path.dirname(os.path.dirname(sys.path[0]))+os.sep+"scripts"
ThisFile    = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.append(ScriptsRoot+os.sep+ThisFile+os.sep+"lib")
sys.path.append(ThisFile+os.sep+"lib")

# import our "library script"
from importsFromImSAnE import *


# reads the 3D coordinates for every pixel, coordinates are in units of microns
realCoords = readRealCoords(xMapFile.getAbsolutePath(),yMapFile.getAbsolutePath(),zMapFile.getAbsolutePath());

# test that sizes match:
checkSize2DarrayVsImgPlus(realCoords, inImp);

# make sure the 'thicknesses values' are sensible
if pxThickness < 1:
	pxThickness = 1
if pxExtraThickness < 0:
	pxExtraThickness = 0

print("calculating the 3D image size...")
# search for min&max per axis, while scaling back to pixel units (from the original micron ones)
min=[+99999999999,+99999999999,+99999999999]
max=[-99999999999,-99999999999,-99999999999]
for x in range(0,inImp.width):
	for y in range(0,inImp.height):
		coord = realCoords[x][y]
		# first, scale to pixel units
		coord[0] = coord[0] / pxSize
		coord[1] = coord[1] / pxSize
		coord[2] = coord[2] / pxSize

		# second, update coordinate bounds
		if (coord[0] < min[0]):
			min[0]=coord[0];
		if (coord[1] < min[1]):
			min[1]=coord[1];
		if (coord[2] < min[2]):
			min[2]=coord[2];
		if (coord[0] > max[0]):
			max[0]=coord[0];
		if (coord[1] > max[1]):
			max[1]=coord[1];
		if (coord[2] > max[2]):
			max[2]=coord[2];

print("detected intervals:")
print("X: "+str(min[0])+" .. "+str(max[0]))
print("Y: "+str(min[1])+" .. "+str(max[1]))
print("Z: "+str(min[2])+" .. "+str(max[2]))

# create an output image of float type (as float can store also integers)
min[0]=math.floor(min[0] /dsRatio)
min[1]=math.floor(min[1] /dsRatio)
min[2]=math.floor(min[2] /dsRatio)

max[0]=math.ceil(max[0] /dsRatio)
max[1]=math.ceil(max[1] /dsRatio)
max[2]=math.ceil(max[2] /dsRatio)

# calc image size and downscale for the final output image
xSize = int(max[0]-min[0]+1)
ySize = int(max[1]-min[1]+1)
zSize = int(max[2]-min[2]+1)

print("creating 3D of sizes: "+str(xSize)+" x "+str(ySize)+" x "+str(zSize))
outFloatProcessors = [ FloatProcessor(xSize,ySize) for z in range(zSize) ]
outFloatPixels = [ outFloatProcessors[z].getPixels() for z in range(len(outFloatProcessors)) ]

# sweep through the inImp and project pixels to outImp
print("populating the 3D image...")
totalX = float(inImp.width)
inIP = inImp.getProcessor();
for x in range(0,inImp.width):
	IJ.showProgress(float(x)/totalX)
	for y in range(0,inImp.height):
		# orig unscaled 3D coords
		coord = realCoords[x][y]

		# normalized vector towards the coordinates centre
		dz = math.sqrt(coord[0]*coord[0] + coord[1]*coord[1] + coord[2]*coord[2]) /dsRatio
		dx = -coord[0] / dz
		dy = -coord[1] / dz
		dz = -coord[2] / dz

		# the outer main (image) layer
		#
		# prefetch the value to be inserted
		origValue = inIP.getf(x,y)
		for t in range(pxThickness):
			# orig coords (at various slices levels) (must be downscaled)
			px = coord[0] + t*dx
			py = coord[1] + t*dy
			pz = coord[2] + t*dz

			nx = int(math.floor((px +0.5) /dsRatio) -min[0])
			ny = int(math.floor((py +0.5) /dsRatio) -min[1])
			nz = int(math.floor((pz +0.5) /dsRatio) -min[2])

			outFloatPixels[nz][nx + ny*xSize] = origValue

		# the inner extra (blocking) layer
		#
		for t in range(pxThickness,pxThickness+pxExtraThickness):
			# orig coords (at various slices levels) (must be downscaled)
			px = coord[0] + t*dx
			py = coord[1] + t*dy
			pz = coord[2] + t*dz

			nx = int(math.floor((px +0.5) /dsRatio) -min[0])
			ny = int(math.floor((py +0.5) /dsRatio) -min[1])
			nz = int(math.floor((pz +0.5) /dsRatio) -min[2])

			outFloatPixels[nz][nx + ny*xSize] = valExtraThickness

print("constructing the 3D image...")
stack = ij.ImageStack(xSize,ySize)
for fp in outFloatProcessors:
	stack.addSlice(fp)

outImp = ij.ImagePlus("back-projected "+inImp.getTitle(), stack)

print("showing the 3D image, done afterwards")
outImp.show()
