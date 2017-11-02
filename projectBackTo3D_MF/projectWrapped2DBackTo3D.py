#@ImagePlus (label="Image to back-projected:") inImp
#@File (label="X coordinate map:") xMapFile
#@File (label="Y coordinate map:") yMapFile
#@File (label="Z coordinate map:") zMapFile

# This script creates a 3D image that displays the original image before
# it got wrapped/embedded into the input inImp 2D image.
# The input image can be any scalar voxel type.

# Usage:
# 	- Find suitable parameters with CountBigNuclei_FindParameter.py
#	- Run Fiji
# 	- Make sure that the update site SCF-MPI-CBG is activated
#	- Run this script

from ij import IJ
from ij.gui import NewImage
from ij import ImagePlus
import math
import os
import sys

# sys.path.append(os.path.abspath("/Users/ulman/p_Akanksha/git_repo/distanceInvolved_MF"))
# from realCoords import *
execfile("/Users/ulman/p_Akanksha/git_repo/distanceInvoled_MF/realCoords.py")
execfile("/Users/ulman/p_Akanksha/git_repo/areaInvolved_MF/realAreas.py")


# reads the 3D coordinates for every pixel, coordinates are in units of microns
realCoords = readRealCoords(xMapFile.getAbsolutePath(),yMapFile.getAbsolutePath(),zMapFile.getAbsolutePath());

# test that sizes match:
checkSize2DarrayVsImgPlus(realCoords, inImp);


# search for min&max per axis, while scaling back to pixel units (from the original micron ones)
min=[+99999999999,+99999999999,+99999999999]
max=[-99999999999,-99999999999,-99999999999]
for x in range(0,inImp.width):
	for y in range(0,inImp.height):
		coord = realCoords[x][y]
		# first, scale to pixel units
		coord[0] = coord[0] / 0.38;
		coord[1] = coord[1] / 0.38;
		coord[2] = coord[2] / 0.38;

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
min[0]=math.floor(min[0])
min[1]=math.floor(min[1])
min[2]=math.floor(min[2])

max[0]=math.ceil(max[0])
max[1]=math.ceil(max[1])
max[2]=math.ceil(max[2])

xSize = int(max[0]-min[0]+1)
ySize = int(max[1]-min[1]+1)
zSize = int(max[2]-min[2]+1)

print("creating 3D of sizes: "+str(xSize)+" x "+str(ySize)+" x "+str(zSize))
outImp = NewImage.createFloatImage("back-projected "+inImp.getTitle(), xSize,ySize,zSize, NewImage.FILL_BLACK)

# sweep through the inImp and project pixels to outImp
print("populating the 3D image...")
inIP = inImp.getProcessor();
for x in range(0,inImp.width):
	for y in range(0,inImp.height):
		coord = realCoords[x][y]
		nx = int(math.floor(coord[0] +0.5) -min[0])
		ny = int(math.floor(coord[1] +0.5) -min[1])
		nz = int(math.floor(coord[2] +0.5) -min[2])

		outImp.setZ(nz+1);
		outImp.getProcessor().setf(nx,ny, inIP.getf(x,y))

print("showing the 3D image, done")
outImp.show()
