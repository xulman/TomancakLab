#@File (style="directory", label="Folder with maps:") mapFolder
#@float (label="Downscale output image by this factor:", value="1.0", min="1") downScaleFactor
#@float (label="Micron radius of the circles:", min="0", value="10") circRadius
#@int (label="Stepping in degrees when rendering circles:", min="0", max="360", value="30") circAngStep
#@boolean (label="Connect perimetr points with lines:", value="True") circPeriLines
#@int (label="Distance between circles along axis X:", min="1", value="20") xGridStep
#@int (label="Distance between circles along axis Y:", min="1", value="20") yGridStep
#@int (label="Position of 1st circle from top-left along axis X:", min="0", value="0") xGridShift
#@int (label="Position of 1st circle from top-left along axis Y:", min="0", value="0") yGridShift

class SimpleFile:
	def __init__(self,path):
		self.path = path
	def getAbsolutePath(self):
		return self.path

aMapFile = SimpleFile(mapFolder.getAbsolutePath()+"/cylinder1_area.txt")
xMapFile = SimpleFile(mapFolder.getAbsolutePath()+"/cylinder1coords_X.txt")
yMapFile = SimpleFile(mapFolder.getAbsolutePath()+"/cylinder1coords_Y.txt")
zMapFile = SimpleFile(mapFolder.getAbsolutePath()+"/cylinder1coords_Z.txt")

from ij import IJ
from ij import ImagePlus
from ij.process import FloatProcessor

# this section adds a folder, in which this very script is living,
# to the current search paths so that we can import our "library script"
import sys.path
import os.path
import inspect
ScriptsRoot = os.path.dirname(os.path.dirname(sys.path[0]))+os.sep+"scripts"
ThisFile    = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.append(ScriptsRoot+os.sep+ThisFile+os.sep+"lib")
sys.path.append(ThisFile+os.sep+"lib")

# import our "library scripts"
from importsFromImSAnE import *
from properMeasurements import *

# from [fx,fy] to [tx,ty] with color in the img (represented as imgBuffer and imgWidth)
def drawLine(fx,fy, tx,ty, color,imgBuffer,imgWidth):
	# that many steps to draw this line
	LL = int(math.floor( math.sqrt((fx-tx)*(fx-tx) + (fy-ty)*(fy-ty)) ))

	dx = float(tx-fx) / float(LL)
	dy = float(ty-fy) / float(LL)
	for s in range(LL):
		cx = fx + int(math.floor( float(s)*dx ))
		cy = fy + int(math.floor( float(s)*dy ))

		imgBuffer[cy*imgWidth +cx] = color
	imgBuffer[ty*imgWidth +tx] = color


def main():
	# reads the area_per_pixel information, already in squared microns
	realSizes = readRealSizes(aMapFile.getAbsolutePath())

	# read the 'real Coordinates', that take into account the different pixel sizes
	realCoordinates = readRealCoords(xMapFile.getAbsolutePath(),yMapFile.getAbsolutePath(),zMapFile.getAbsolutePath())

	w = len(realSizes)
	h = len(realSizes[0])
	print("calculating from maps in the folder: "+mapFolder.getAbsolutePath())
	print(" maps  width="+str(w)+", heigh="+str(h))

	w = int(math.ceil( w / downScaleFactor ))
	h = int(math.ceil( h / downScaleFactor ))
	print("output width="+str(w)+", heigh="+str(h))

	OutputPixels = [ 0.0 for o in range(w*h) ]

	# grid positions - in downscaled image
	for y in range(2+yGridShift, h-2, yGridStep):
		for x in range(2+xGridShift, w-2, xGridStep):
			periPoints = []

			for ang in range(0,359,circAngStep):
				angInRad = float(ang)*3.14159/180.0
				direction = [ math.cos(angInRad),math.sin(angInRad) ]

				initPos = [ x *downScaleFactor,y *downScaleFactor ]
				endPos  = travelGivenRealDistance(initPos, direction, circRadius, realCoordinates)

				# convert back into the output image
				cx = int(math.floor(endPos[0] /downScaleFactor))
				cy = int(math.floor(endPos[1] /downScaleFactor))

				#if cx >= 0 and cx < w and cy >= 0 and cy < h:
				periPoints.append( [cx,cy] )

			color = 1
			if circPeriLines:
				lastValidIdx = len(periPoints)-1
				for p in range(lastValidIdx):
					drawLine(periPoints[p][0],periPoints[p][1], periPoints[p+1][0],periPoints[p+1][1], color, OutputPixels,w)
				drawLine(periPoints[lastValidIdx][0],periPoints[lastValidIdx][1], periPoints[0][0],periPoints[0][1], color, OutputPixels,w)
			else:
				for p in periPoints:
					OutputPixels[p[1]*w +p[0]] = color

	ImagePlus("Resolution circles", FloatProcessor(w,h, OutputPixels)).show()


main()
