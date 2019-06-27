from ij import IJ
from ij import ImagePlus
import sys
import math

def getPixelAtRealPos(array, x,y):
	# returns bilinearily interpolated value/vector at [x,y]
	# from the array of values/vectors

	# some existing nearby pixel: bottom-left corner
	X = int(math.floor(x))
	Y = int(math.floor(y))

	# diagonal, top-right corner
	X2 = X+1
	Y2 = Y+1

	# axial distances from the bottom-left corner
	x = float(x-X)
	y = float(y-Y)

	# array[X][Y] is assumed to be an array again
	N = len(array[X][Y])

	# build output array (of length N)
	res = []
	for i in range(N):
		# bilinearily interpolated value
		val  = float(array[X ][Y ][i]) * (1.0-x)*(1.0-y)
		val += float(array[X ][Y2][i]) * (1.0-x)*(    y)
		val += float(array[X2][Y ][i]) * (    x)*(1.0-y)
		val += float(array[X2][Y2][i]) * (    x)*(    y)
		res.append(val)

	return res


# ---------- real distances ----------
def properLength(xyCoords, realCoordinates):
	# xyCoords should be a list of pairs,
	# realCoordinates should be a 2D list of tripples
	# (e.g., obtained via importsFromImSAnE.readRealCoords())
	#
	# xyCoords is essentially a segmented curve whose nodes/vertices are listed here

	# overall sum
	sum = 0.0

	for idx in range(1,len(xyCoords)):
		# embedded 2D coords of the current line segment
		a = xyCoords[idx-1]
		b = xyCoords[idx  ]
		#print "[ "+str(a[0])+" , "+str(a[1])+" ] --> [ "+str(b[0])+" , "+str(b[1])+" ]"

		# the proper/original 3D coords of the current line segment...
		aXYZ = getPixelAtRealPos(realCoordinates, a[0],a[1])
		bXYZ = getPixelAtRealPos(realCoordinates, b[0],b[1])
		#print "[ "+str(aXYZ[0])+" , "+str(aXYZ[1])+" , "+str(aXYZ[2])+" ] -> [ "+str(bXYZ[0])+" , "+str(bXYZ[1])+" , "+str(bXYZ[2])+" ]"

		# ...are subtracted from each other...
		dx = aXYZ[0] - bXYZ[0]
		dy = aXYZ[1] - bXYZ[1]
		dz = aXYZ[2] - bXYZ[2]

		# ...and length is calculated
		dist = math.sqrt(dx*dx + dy*dy + dz*dz)
		sum += dist

	return sum


def travelGivenRealDistance(xyStartCoords, xyDirection, micronDistance, realCoordinates):
	# xyStartCoords should be a 2-element list of starting x,y position
	# xyDirection should be a 2-element list of (small) steps to do until one get sufficiently far
	# micronDistance is how far we should get (aka target distance):
	#  if the current step induces distance closer to the target one, no further steps are conducted;
	#  if the next step would induce a distance closer than the current one, we move
	# return value is [x,y] with the new position, it is always inside the image

	noGoBorder = 2
	w = len(realCoordinates)    -noGoBorder
	h = len(realCoordinates[0]) -noGoBorder

	cx = xyStartCoords[0]
	cy = xyStartCoords[1]
	dist = 0.0

	shouldMove = True
	while shouldMove:
		# where shall be the new step
		ncx = cx+xyDirection[0]
		ncy = cy+xyDirection[1]

		# if the new step would ended up outside the image,
		# we better break the while cycle and return the last valid position
		if ncx < noGoBorder or ncx >= w or ncy < noGoBorder or ncy >= h:
			break

		# examine what distance would there be if we would have moved more step
		nextSegment = [ [cx,cy],[ncx,ncy] ]
		nextDist  = properLength(nextSegment, realCoordinates)
		nextDist += dist

		# have we crossed over the threshold distance?
		if nextDist < micronDistance:
			# no, we can update the current step
			cx = ncx
			cy = ncy
			dist = nextDist
		else:
			# yes, we need to stop iterating in any case
			shouldMove = False

			# shall we use the distance?
			if micronDistance-dist > nextDist-micronDistance:
				# yes, the new one
				cx = ncx
				cy = ncy
				dist = nextDist

	return [ cx,cy ]


# ---------- real areas ----------
def properArea(xyCoords, realAreas):
	# xyCoords should be a list of pairs,
	# realAreas should be a 2D list of scalars
	# (e.g., obtained via importsFromImSAnE.readRealSizes())
	#
	# xyCoords is essentially a list of pixels that represent one object/component

	# overall sum
	sum = 0.0

	for xy in xyCoords:
		sum += realAreas[xy[0]][xy[1]]

	return sum


# ---------- aux functions ----------
def writeCoordsToFile(xyCoords, filename):
	f = open(filename,"w")
	for c in xyCoords:
		f.write(str(c[0])+" "+str(c[1])+"\n")
	f.close()
