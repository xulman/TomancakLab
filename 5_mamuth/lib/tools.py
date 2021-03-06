from __future__ import print_function
import math

# ------------------------------------------------------------------------------------
def parseOutTimes(tps):
	out = []

	while len(tps) > 0:

		# find the next ',' or '-'
		ic = tps.find(',')
		ih = tps.find('-')

		#print "found , @ " + str(ic) + " and - @ " + str(ih)

		# -1 means 'not found'
		if ic == -1:
			# processing for sure the last term
			ic = len(tps)

		# make sure if hyphen is not found to go to the "comma branch"
		if ih == -1:
			ih = ic+1


		# take the one that is closer to the beginning
		if ic < ih:
			# we're parsing out N,
			N = int(tps[0:ic])

			out.append(N)
			tps = tps[ic+1:]

			print("parsed out: single timepoint "+str(N))
		else:
			# we're parsing out N-M,
			N = int(tps[0:ih])
			M = int(tps[ih+1:ic])

			for i in range(N,M+1):
				out.append(i)

			tps = tps[ic+1:]

			print("parsed out: timepoint interval "+str(N)+" to "+str(M))

	out.sort()

	# ww = out.unique()
	ww = []
	for i in range(len(out)):
		if i == 0 or out[i-1] != out[i]:
			ww.append(out[i])

	return ww

# ------------------------------------------------------------------------------------
# this is essentially only a wrapper/binder of pixel data (reachable
# as [z][y*xSize+x]) and the relevant metadata
class SimpleImg:
	def __init__(self,pixels,xSize,ySize,zSize):
		self.pxls = pixels
		self.xSize = xSize
		self.ySize = ySize
		self.zSize = zSize

	def setPixelsToZero(self):
		for z in range(len(self.pxls)):
			slc = self.pxls[z]
			for i in range(len(slc)):
				slc[i] = 0

# ------------------------------------------------------------------------------------
def drawBall(xC,yC,zC, R,Col, img):
	drawBall(xC,yC,zC, R,Col, img,1.0)

# ------------------------------------------------------------------------------------
# draws ball of diameter D with center xC,yC,zC with colour Col into the image
# considering the Down-scale factor, the image has to be of the SimpleImg type
def drawBall(xC,yC,zC, D,Col, img,Down):
	xC = int(math.ceil(xC / Down))
	yC = int(math.ceil(yC / Down))
	zC = int(math.ceil(zC / Down))
	R  = int(math.ceil( D / (2.0*Down) ))

	#print("SPOT: "+str(xC)+","+str(yC)+","+str(zC)+" r="+str(R)+" @ ID="+str(Col))

	x_min = xC-R if xC > R           else 0
	x_max = xC+R if xC+R < img.xSize else img.xSize-1

	y_min = yC-R if yC > R           else 0
	y_max = yC+R if yC+R < img.ySize else img.ySize-1

	z_min = zC-R if zC > R           else 0
	z_max = zC+R if zC+R < img.zSize else img.zSize-1

	R2 = R*R

	# sweep the bounds and draw the ball
	for x in range(x_min,x_max+1):
		dx = (x-xC) * (x-xC)

		for y in range(y_min,y_max+1):
			dxy = dx + ((y-yC) * (y-yC))

			for z in range(z_min,z_max+1):
				dz = (z-zC) * (z-zC)

				if dxy+dz <= R2:
					img.pxls[z][x + y*img.xSize] = Col

# ------------------------------------------------------------------------------------
def drawLine(xC,yC,zC, xD,yD,zD, R,Col, img):
	drawLine(xC,yC,zC, xD,yD,zD, R,Col, img,1.0)

# ------------------------------------------------------------------------------------
# draws a line made of many (overlapping) balls, of width R, from
# [xC,yC,zC] to [xD,yD,zD], with color Col, into the image img considering
# the Down-scale factor, the image has to be of the SimpleImg type
def drawLine(xC,yC,zC, xD,yD,zD, R,Col, img,Down):
	# the line length (LL)
	LL = math.sqrt((xC-xD)*(xC-xD) + (yC-yD)*(yC-yD) + (zC-zD)*(zC-zD))

	# how many up-to-R-long segments are required
	SN = math.ceil(LL / R)

	# if "line is decimated into a point", just draw one spot
	if SN == 0:
		drawBall(xC,yC,zC,R*Down,Col,img,Down)
		# NB: the coordinates and _radius_ will get divided by Down,
		#     but we want R to represent already the final radius
		return

	# (real) length of one segment
	SS = LL / SN

	# a "one segment" vector
	xSV = (xD-xC)*SS/LL
	ySV = (yD-yC)*SS/LL
	zSV = (zD-zC)*SS/LL

	SN = int(SN)
	for i in range(0,SN+1):
		x = xC  +  float(i)*xSV
		y = yC  +  float(i)*ySV
		z = zC  +  float(i)*zSV

		drawBall(x,y,z,R*Down,Col,img,Down)
