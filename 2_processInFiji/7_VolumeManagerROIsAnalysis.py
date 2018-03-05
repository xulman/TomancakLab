
# This script counts the nuclei in a given ROI over time.
# It takes a folder of binary images and the ROI as input, and then displays a table
# in which the number of nuclei for each timestamp is saved.

# Usage:
# 	- Run Fiji
#	- Make sure that the update site SCF-MPI-CBG is activated
# 	- Open one of your images
# 	- Select the Area of Interest
#	- Run this script
#	- Choose the folder with all your input images


from ij import IJ
import ij.ImagePlus
from ij.gui import Roi
from ij.io import DirectoryChooser
from ij.measure import ResultsTable
from ij.process import ByteProcessor
import os
import sys

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

import de.mpicbg.scf.volumemanager.VolumeManager
import de.mpicbg.scf.imgtools.geometry.data.PolylineSurface

#Get ROI
#bigImg = IJ.getImage()
#RoiD  = ij.ImagePlus.getRoi(bigImg)

#if RoiD != None:
#	print RoiD

# TODO: prompt user to open and populate/load the Volume Manager with the correct data
#       and wait for "ok" button to continue

# current volume manager instance
vm = de.mpicbg.scf.volumemanager.VolumeManager.getInstance()

# returns PolylineSurface for given idx (=volume inside the VolumeManager)
def getVolume(idx):
	vm.setSelectedIndex(idx);
	if (vm.getSelectedIndex() != idx):
		return None

	return vm.getCurrentVolume()


# returns ROI from the given PolylineSurface (ps) and slice
# returns None if no surface defined for the given slice
def getROI(ps,slice):
	if ps is None:
		return None

	roi = ps.getRoi(slice)
	if roi is None:
		roi = ps.getInterpolatedRoi(slice,False)
# debug:
#		if roi is not None:
#			print str(slice)+": getting interpolated ROI"
#		else:
#			print str(slice)+": no ROI obtained"
#	else:
#		print str(slice)+": getting real full ROI"
	return roi


# scan through all slices of the image, through all volumes and process respective ROIs
image = IJ.getImage();
width = image.getWidth()
height = image.getHeight()

idx = 0
ps = getVolume(idx)

table = ResultsTable()

while ps is not None:
	print "------------- "+str(idx)+". volume -------------"
	for z in range(1,image.getNSlices()+1):
		roi = getROI(ps,z)

		if roi is not None:
			# process the roi
			print "roi at slice "+str(z)
			points = roi.getContainedPoints()
			# we can calc proper Area from points

			# perimeter?
			polygon = roi.getInterpolatedPolygon()

			table.incrementCounter()
			table.addValue('Volume no.',idx)
			table.addValue('Slice no.',z)
			table.addValue('ROI area (px^2)',len(points))
			table.addValue('ROI perimeter (px)',polygon.npoints)

			# debug:
			BP = ByteProcessor(width,height);
			pixels = BP.getPixels()
			# area
			for p in points:
				pixels[p.x + p.y*width] = 100+idx
			# outline (a bit below)
			for i in range(0,polygon.npoints):
				x = int(polygon.xpoints[i])
				y = int(polygon.ypoints[i]) +500
				pixels[x + y*width] = 100+idx
			# show the image
			newImg = ImagePlus("vol "+str(idx)+", slice "+str(z),BP)
			newImg.show()

	# next volume...
	idx += 1
	ps = getVolume(idx)

table.show('Results')
