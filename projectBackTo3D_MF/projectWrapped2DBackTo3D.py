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
import math
import os
import sys

# sys.path.append(os.path.abspath("/Users/ulman/p_Akanksha/git_repo/distanceInvolved_MF"))
# from realCoords import *
execfile("/Users/ulman/p_Akanksha/git_repo/distanceInvoled_MF/realCoords.py")
execfile("/Users/ulman/p_Akanksha/git_repo/areaInvolved_MF/realAreas.py")



# reads the area_per_pixel information, already in squared microns
realCoords = readRealCoords(xMapFile.getAbsolutePath(),yMapFile.getAbsolutePath(),zMapFile.getAbsolutePath());

# test that sizes match:
checkSize2DarrayVsImgPlus(realCoords, inImp);

# see CorrectedNeigh for examples on how to surf input image and create output image
