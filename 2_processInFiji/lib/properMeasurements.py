from ij import IJ
from ij import ImagePlus
import sys
import math

def getPixelAtRealPos(array, x,y):
	# some existing nearby pixel
	X = int(math.floor(x))
	Y = int(math.floor(y))

	# array[X][Y] is assumed to be an array again
	N = len(array[X][Y])

	# build output array (of length N)
	res = []
	for i in range(N):
		res.append(array[X][Y][i])

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
		print "[ "+str(a[0])+" , "+str(a[1])+" ] -> [ "+str(b[0])+" , "+str(b[1])+" ]"

		# the proper/original 3D coords of the current line segment...
		aXYZ = getPixelAtRealPos(realCoordinates, a[0],a[1])
		bXYZ = getPixelAtRealPos(realCoordinates, b[0],b[1])
		print "[ "+str(aXYZ[0])+" , "+str(aXYZ[1])+" , "+str(aXYZ[2])+" ] -> [ "+str(bXYZ[0])+" , "+str(bXYZ[1])+" , "+str(bXYZ[2])+" ]"

		# ...are subtracted from each other...
		dx = aXYZ[0] - bXYZ[0]
		dy = aXYZ[1] - bXYZ[1]
		dz = aXYZ[2] - bXYZ[2]

		# ...and length is calculated
		dist = math.sqrt(dx*dx + dy*dy + dz*dz)
		sum += dist

	return sum


# ---------- real areas ----------
