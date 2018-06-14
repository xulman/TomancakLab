from __future__ import print_function
#@File (label="Input Mamuth XML file:") xmlFile
#@File (style="directory", label="Output folder:") tifFolder
#@int (label="Original image X size:") xSize
#@int (label="Original image Y size:") ySize
#@int (label="Original image Z size:") zSize
#@int (label="Downsampling factor:") xDown
#@boolean (label="Write also CTC tracks.txt:") shouldWriteCTCTRACKS

from ij import IJ
import ij.ImagePlus
import ij.ImageStack
from ij.process import ShortProcessor
import math

# this section adds a folder, in which this very script is living,
# to the current search paths so that we can import any script living next to this one
import sys.path
import os.path
import inspect
sys.path.append(os.path.dirname(inspect.getfile(inspect.currentframe())))
from MamutXMLreader import *


# adjust the size of the output image immediately
Down = float(xDown)
xSize = int(math.ceil(xSize / Down))
ySize = int(math.ceil(ySize / Down))
zSize = int(math.ceil(zSize / Down))


# ------------------------------------------------------------------------------------
# draws ball of radius R with center xC,yC,zC with colour Col into the image
def drawBall(xC,yC,zC,R,Col,img):
	xC = int(math.ceil(xC / Down))
	yC = int(math.ceil(yC / Down))
	zC = int(math.ceil(zC / Down))
	R  = int(math.ceil(R  / Down))

	print("SPOT: "+str(xC)+","+str(yC)+","+str(zC)+" r="+str(R)+" @ ID="+str(Col))

	x_min = xC-R if xC > R       else 0
	x_max = xC+R if xC+R < xSize else xSize

	y_min = yC-R if yC > R       else 0
	y_max = yC+R if yC+R < ySize else ySize

	z_min = zC-R if zC > R       else 0
	z_max = zC+R if zC+R < zSize else zSize

	R2 = R*R

	# sweep the bounds and draw the ball
	for x in range(x_min,x_max+1):
		dx = (x-xC) * (x-xC)

		for y in range(y_min,y_max+1):
			dxy = dx + ((y-yC) * (y-yC))

			for z in range(z_min,z_max+1):
				dz = (z-zC) * (z-zC)

				if dxy+dz <= R2:
					img[z][x + y*xSize] = Col


# ------------------------------------------------------------------------------------
# the main work happens here
def main():

	# --- this parses the data in ---
	[minT,maxT] = readInputXMLfile(xmlFile.getAbsolutePath())

	# now, we have a list of roots & we have neighborhood-ships,
	# let's reconstruct the trees from their roots,
	# in fact we do a depth-first search...
	lastID = 0
	for root in ROOTS:
		print("extracted tree ID="+str(root))
		lastID = followTrack(ROOTS[root],lastID+1)
	# --- this parses the data in ---


	# create the output image (only once cause it is slow)
	outShortProcessors = [ ShortProcessor(xSize,ySize) for z in range(zSize) ]
	img = [ outShortProcessors[z].getPixels() for z in range(len(outShortProcessors)) ]

	stack = ij.ImageStack(xSize,ySize)
	for sp in outShortProcessors:
		stack.addSlice(sp)

	outImp = ij.ImagePlus("markers preview", stack)
	outImp.show()
	#NB: the img is essentially a "python overlay" over the IJ1 image stack's pixel data

	print("detected interval of time points ["+str(minT)+","+str(maxT)+"]")

	# now scan over the range of time points and draw points
	for t in range(minT,maxT+1):
		# filename:
		fn = tifFolder.getAbsolutePath()+"/time{0:03d}.tif".format(t)
		print("Writing file: "+fn)

		# prepare -> reset -> zero the output image
		for plane in img:
			for i in range(len(plane)):
				plane[i] = 0

		# scan all tracks
		for tID in TRACKS:
			TRACK = TRACKS[tID]

			# does this track has the current timepoint?
			if t in TRACK:
				spot = SPOTS[TRACK[t]]
				drawBall(spot[0],spot[1],spot[2],spot[4],tID,img)

		# now write the image onto harddrive...
		IJ.save(outImp,fn)

	# lastly, save also the CTC tracks.txt if requested so
	if shouldWriteCTCTRACKS:
		fn = tifFolder.getAbsolutePath()+"/tracks.txt"
		print("Writing file: "+fn)
		writeCTCTRACKS(fn)


main()
