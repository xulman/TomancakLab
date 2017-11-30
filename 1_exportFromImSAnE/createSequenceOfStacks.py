#@File (style="directory", label="Input directory FROM") inputDirFrom
#@File (style="directory", label="Input directory   TO") inputDirTo
#@String (label="path between input dirs and slice images", value="cylinder1_index/cylinder1") subPath
#@File (style="directory", label="Output directory to store stacks") outputDir
#@int (label="First time-point to be used", value="1") timeSpanFrom
#@int (label="Last  time-point to be used", value="2") timeSpanTo

# Consider folder holding multiple folders 'data_layer_m*' and 'data_layer_p*',
# each having (somewhere deep inside in nested folders) a time-lapse sequence
# of 2D images. The user is assumed to choose two such 'data_layer_*' folders
# and this script will iterate between them considering every single one as a
# z-slice of some future stack. But since inside them are time-lapse sequences
# of images, the output is also a time-lapse sequence of stacks of these images:
# for every time point T take every folder F from the respective 'data_layer_*'
# folders and create a stack from slices/images "$F/$subPath/cmp_1_1_T$T.tif"

# Usage:
# 	- Run Fiji
#	- Run this script
#	- Choose the input folders and ranges
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

# create a list of folders F:
# extract [pm][:digit:] pattern to determine indices
# FROM FOLDER
s = inputDirFrom.getPath()
i = s.rfind("data_layer_")
if (i == -1):
	print "haven't find 'data_layer_' in the path of inputDirFrom"
	# break the script here TODO

pat = s[i+11] + s[i+12]
if (i+13 < len(s)):
	pat += s[i+13]

orderDict = ["p20","p19","p18","p17","p16","p15","p14","p13","p12","p11","p10","p9","p8","p7","p6","p5","p4","p3","p2","p1","m1","m2","m3","m4","m5","m6","m7","m8","m9","m10","m11","m12","m13","m14","m15","m16","m17","m18","m19","m20"]
zFrom = -1
for i in range(len(orderDict)):
	if (pat.find(orderDict[i]) > -1):
		zFrom = i;

if (zFrom == -1):
	print "haven't recognized '"+pat+"' in the path of inputDirFrom"
	# break the script here TODO

# TO FOLDER
s = inputDirTo.getPath()
i = s.rfind("data_layer_")
if (i == -1):
	print "haven't find 'data_layer_' in the path of inputDirTo"
	# break the script here TODO

pat = s[i+11] + s[i+12]
if (i+13 < len(s)):
	pat += s[i+13]

zTo = -1
for ii in range(len(orderDict)):
	if (pat.find(orderDict[ii]) > -1):
		zTo = ii;

if (zTo == -1):
	print "haven't recognized '"+pat+"' in the path of inputDirTo"
	# break the script here TODO

# a list of time points
for TT in range(timeSpanFrom,timeSpanTo+1):
	T = '%(time)03d' % { 'time' : TT }

	# create an empty stack

	for FF in range(zFrom,zTo+1):
		# a list of folders
		F = inputDirTo.getPath()
		F = F[0:i+11] + orderDict[FF] + "/" + subPath + "/cmp_1_1_T" + T + ".tif"
		print F

		# read slice image and add it

	# save the stack
	F = outputDir.getPath() + "/cmp_3D_T" + T + ".tif"
	print F

