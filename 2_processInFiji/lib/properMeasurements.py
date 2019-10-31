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


# assuming the A,B,C are 2D vertices of a triangle in CCW order
def createProper2dTriangle(A,B,C, realCoordinates):
	# s as surface, sA will be a 3D coordinate
	sA = getPixelAtRealPos(realCoordinates, A[0],A[1])
	sB = getPixelAtRealPos(realCoordinates, B[0],B[1])
	sC = getPixelAtRealPos(realCoordinates, C[0],C[1])

	# bring sA (and the whole triangle) to [0,0,0]
	sB[0] -= sA[0]
	sB[1] -= sA[1]
	sB[2] -= sA[2]

	sC[0] -= sA[0]
	sC[1] -= sA[1]
	sC[2] -= sA[2]

	# a triangle in a 2D plane:
	# normalizedAB=[nax,nay] is "x" axis
	# A is at [0,0]
	# B is at [|AB|,0]
	# C is AB rotated by ang, at radius of |AC|

	lenAB = math.sqrt(sB[0]*sB[0] + sB[1]*sB[1] + sB[2]*sB[2])
	lenAC = math.sqrt(sC[0]*sC[0] + sC[1]*sC[1] + sC[2]*sC[2])
	angBAC = math.acos( (sB[0]*sC[0] + sB[1]*sC[1] + sB[2]*sC[2]) / (lenAB*lenAC) )

	# rotate (lenAC,0) by angBAC
	nC = [ lenAC*math.cos(angBAC), -lenAC*math.sin(angBAC) ]
	return [0,0], [lenAB,0], nC


# ---------- aux IO functions ----------
def writeCoordsToFile(xyCoords, filename):
	f = open(filename,"w")
	for c in xyCoords:
		f.write(str(c[0])+" "+str(c[1])+"\n")
	f.close()


# ---------- aux math functions ----------
def crossProduct(vec3elemA, vec3elemB):
	return [ vec3elemA[1] * vec3elemB[2] - vec3elemA[2] * vec3elemB[1],
	         vec3elemA[2] * vec3elemB[0] - vec3elemA[0] * vec3elemB[2],
	         vec3elemA[0] * vec3elemB[1] - vec3elemA[1] * vec3elemB[0] ]

def isCCW(p2dA, p2dB, p2dC):
	vec1 = [ p2dB[0]-p2dA[0], p2dB[1]-p2dA[1] ]
	vec2 = [ p2dC[0]-p2dA[0], p2dC[1]-p2dA[1] ]
	cross_elem2 = vec1[0] * vec2[1] - vec1[1] * vec2[0]
	return cross_elem2 < 0

# note that p2dC is never adjusted, is constant here
def makeCCWorder(p2dA, p2dB, p2dC):
	if isCCW(p2dA, p2dB, p2dC):
		return p2dA, p2dB, p2dC
	else:
		return p2dB, p2dA, p2dC


# row major!  Mat = ( a b )
#                   ( c d )
def matInverse(Mat2DAsArray):
	a = Mat2DAsArray[0]
	b = Mat2DAsArray[1]
	c = Mat2DAsArray[2]
	d = Mat2DAsArray[3]

	det = 1.0 / (a*d - b*c)
	return [ d*det, -b*det, -c*det, a*det ]


# row major!  Mat = ( a b )
#                   ( c d )
def matDet(Mat2DAsArray):
	a = Mat2DAsArray[0]
	b = Mat2DAsArray[1]
	c = Mat2DAsArray[2]
	d = Mat2DAsArray[3]

	return (a*d - b*c)


# row major!  Mat = ( a b )
#                   ( c d )
def matMult(Mat2DAsArrayLeft, Mat2DAsArrayRight):
	q = Mat2DAsArrayLeft[0]
	w = Mat2DAsArrayLeft[1]
	e = Mat2DAsArrayLeft[2]
	r = Mat2DAsArrayLeft[3]

	a = Mat2DAsArrayRight[0]
	s = Mat2DAsArrayRight[1]
	d = Mat2DAsArrayRight[2]
	f = Mat2DAsArrayRight[3]

	return [ q*a+w*d, q*s+w*f, e*a+r*d, e*s+r*f ]


#-------------------------------------------------------------------------
# the following code was cloned (and modified to avoid Numpy requirement
# in order to run in Fiji's Jython) from computeAreaAndElongationNematic()
# by Matthias Merkel, http://www.matthiasmerkel.de
#-------------------------------------------------------------------------
# the columns of this matrix are the two vectors r1-r0 and r2-r0; where ri are the corners of a regular triangle, sorted in ccw direction; the area of the triangle is 1.
_Side0 = 2.0/math.sqrt(math.sqrt(3)) # side of a regular triangle with area 1
RTM = [-0.5*math.sqrt(3) *_Side0, -0.5*math.sqrt(3) *_Side0, 0.5 *_Side0, -0.5 *_Side0]
RTMinvted = matInverse(RTM)

# the method assumes CW order of vertices
def computeAreaAndElongationNematic_nonNumpy(p2dA, p2dB, p2dC):
	curTriangleMatrix = [ p2dB[0] - p2dA[0], p2dC[0] - p2dA[0], p2dB[1] - p2dA[1], p2dC[1] - p2dA[1] ]
	shape = matMult(curTriangleMatrix, RTMinvted)

	area = matDet(shape)
	linScalingFactor = math.sqrt(math.fabs(area))
	theta = math.atan2(shape[2]-shape[1], shape[0]+shape[3])

	n_xx = 0.5*(shape[0]-shape[3])
	n_xy = 0.5*(shape[1]+shape[2])
	twoPhi = theta + 2* 0.5*math.atan2(n_xy, n_xx)

	n_norm = math.sqrt(n_xx*n_xx + n_xy*n_xy)
	normQ = math.asinh(n_norm / linScalingFactor)

	n_xx = normQ*math.cos(twoPhi)
	n_xy = normQ*math.sin(twoPhi)
	n_norm = math.sqrt(n_xx*n_xx + n_xy*n_xy)

	return area, n_norm
#-------------------------------------------------------------------------
