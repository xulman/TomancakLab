#@File (label="Pixel areas map:") aMapFile
#@File (label="X coordinate map:") xMapFile
#@File (label="Y coordinate map:") yMapFile
#@File (label="Z coordinate map:") zMapFile
#@boolean (label="Raster the ROIs into a new image") rasterROIs

# This script does....

# Usage:
# 	- Run Fiji
#	- Make sure that the update site SCF-MPI-CBG is activated
# 	- Open one of your images
# 	- Open SCF's VolumeManager
#	- Run this script


from ij import IJ
import ij.ImagePlus
import ij.ImageStack
from ij.measure import ResultsTable
from ij.process import ByteProcessor
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
from properMeasurements import *

import de.mpicbg.scf.volumemanager.VolumeManager
import de.mpicbg.scf.imgtools.geometry.data.PolylineSurface


# "locate" the currently processed image
image = IJ.getImage()

# TODO: prompt user to open and populate/load the Volume Manager with the correct data
#       and wait for "ok" button to continue

# current volume manager instance
vm = de.mpicbg.scf.volumemanager.VolumeManager.getInstance()


# reads the area_per_pixel information, already in squared microns
realSizes = readRealSizes(aMapFile.getAbsolutePath())

# read the 'real Coordinates', that take into account the different pixel sizes
realCoordinates = readRealCoords(xMapFile.getAbsolutePath(),yMapFile.getAbsolutePath(),zMapFile.getAbsolutePath())

# test that sizes of realSizes and imp matches
checkSize2DarrayVsImgPlus(realSizes, image)
checkSize2DarrayVsImgPlus(realCoordinates, image)


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
width = image.getWidth()
height = image.getHeight()

# a list of output (and yet empty) slices
outByteProcessor = None
if rasterROIs:
	outByteProcessor = [ ByteProcessor(width,height) for z in range(image.getNSlices()) ]

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

			# list of coords that make up this full ROI
			points = roi.getContainedPoints()
			area = 0.0
			for p in points:
				area += realSizes[p.x][p.y]

			# list of coords that make up this ROI's perimeter
			polygon = roi.getInterpolatedPolygon()
			coords = []
			for i in range(0,polygon.npoints):
				coords.append([polygon.xpoints[i],polygon.ypoints[i]])

			# debug: what perimeter points are considered
			# writeCoordsToFile(coords,"/Users/ulman/DATA/7_coords_"+str(idx)+".txt")

			table.incrementCounter()
			table.addValue('Volume no.',idx)
			table.addValue('Slice no.',z)
			table.addValue('ROI area (px^2)',len(points))
			table.addValue('ROI proper area (um^2)',area)
			table.addValue('ROI perimeter (px)',polygon.npoints)
			perLen = properLength(coords,realCoordinates)
			table.addValue('ROI proper perimeter (um)',perLen)
			table.addValue('Circularity (higher more roundish)', (area * 4.0 * math.pi) / (perLen * perLen))

			if rasterROIs:
				pixels = outByteProcessor[z-1].getPixels()
				for p in points:
					pixels[p.x + p.y*width] = 1+idx

#			# debug:
#			BP = ByteProcessor(width,height);
#			pixels = BP.getPixels()
#			# area
#			for p in points:
#				pixels[p.x + p.y*width] = 100+idx
#			# outline (a bit below)
#			for i in range(0,polygon.npoints):
#				x = int(polygon.xpoints[i])
#				y = int(polygon.ypoints[i]) +500
#				pixels[x + y*width] = 100+idx
#			# show the image
#			newImg = ImagePlus("vol "+str(idx)+", slice "+str(z),BP)
#			newImg.show()

	# next volume...
	idx += 1
	ps = getVolume(idx)

table.show('Results')

if rasterROIs:
	stack = ij.ImageStack(width,height)
	for bp in outByteProcessor:
		stack.addSlice(bp)

	newImg = ij.ImagePlus("rasterized ROIs from VolumeManager", stack)
	newImg.show()

