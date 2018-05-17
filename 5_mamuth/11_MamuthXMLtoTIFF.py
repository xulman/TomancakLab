#@File (label="Input Mamuth XML file:") xmlFile
#@File (label="Output TIF file:") tifFile
#@int (label="Output image X size:") xSize
#@int (label="Output image Y size:") ySize
#@int (label="Output image Z size:") zSize


# scans the input file 'f' line by line until it finds a line that matches 'msg',
# and returns this line, or None if end of the file is reached
def advanceFileTillLine(f,msg):
	i = -1
	while i == -1:
		line = f.readline()
		if not line:
			return None

		i = line.find(msg)

	return line


# for processing of trackPairs
def parseOutRangePair(rangeStr):
	i = rangeStr.find('-')
	if (i == -1):
		print "haven't find the range separator '-', returning None instead"
		return None

	q = int(rangeStr[0:i])
	w = int(rangeStr[i+1:len(rangeStr)])
	return [q,w]


# scans the input string 'msg' for the first pattern "N" that occurs after position 'idx'
# in the string, and returns the N, or 0 if the pattern is not found
def parseOutNumber(msg, idx=0):
	# find the first occurence of "
	i = msg.find('"',idx)
	if i == -1:
		return 0

	# trim the string and find yet another (second) occurence of "
	msg = msg[i+1:len(msg)]
	i = msg.find('"')
	if i == -1:
		return 0

	return float(msg[0:i])


# ------------------------------------------------------------------------------------
# draws ball of radius R with center xC,yC,zC with colour Col into the image img[x][y][z]
def drawBall(xC,yC,zC,R,Col,img):
	print "SPOT: "+str(xC)+","+str(yC)+","+str(zC)+" @ ID="+str(Col)

def drawBall_REAL(xC,yC,zC,R,Col,img):
	x_min = xC-R if xC > R       else 0
	x_max = xC+R if xC+R < xSize else xSize

	y_min = yC-R if yC > R       else 0
	y_max = yC+R if yC+R < ySize else ySize

	z_min = zC-R if zC > R       else 0
	z_max = zC+R if zC+R < zSize else zSize

	R2 = R*R

	# sweep the bounds and draw the ball
	for z in range(z_min,z_max+1):
		dz = (z-zC) * (z-zC)

		for y in range(y_min,y_max+1):
			dyz = dz + ((y-yC) * (y-yC))

			for x in range(x_min,x_max+1):
				dx = (x-xC) * (x-xC)

				if dx+dyz <= R2:
					img[x][y][z] = col


def createImage(xs,ys,zs):
	img = [[[0 for z in range(xs)] for y in range(ys)] for x in range(zs)]
	return img


# ------------------------------------------------------------------------------------
# the main work happens here
def main():

	#OutputPixels = [[[0 for z in range(xSize)] for y in range(ySize)] for x in range(zSize)]
	# open the output file
	fn = tifFile.getAbsolutePath()
	print "Writing file: "+fn

	# open the input file
	f = open(xmlFile.getAbsolutePath(),"r")


	# scan the input file until it finds begining of the definitions of spots
	line = advanceFileTillLine(f,"AllSpots nspots=")

	# read out the number of spots
	nSpots = int(parseOutNumber(line))

	# read out all spots definitions
	SPOTS = {}
	for cntSpots in range(nSpots):
		line = advanceFileTillLine(f,"Spot ID")
		sID = int(parseOutNumber(line))

		idx = line.find("POSITION_X=")
		sX  = parseOutNumber(line,idx)

		idx = line.find("POSITION_Y=")
		sY  = parseOutNumber(line,idx)

		idx = line.find("POSITION_Z=")
		sZ  = parseOutNumber(line,idx)

		idx = line.find("FRAME=")
		sT  = int(parseOutNumber(line,idx))

		idx = line.find("RADIUS=")
		sR  = parseOutNumber(line,idx)

		# save the currently extracted spot
		SPOTS[sID] = [sX,sY,sZ,sT,sR]

	# span of the time-points:
	minTime = -9999;
	maxTime = -9999;


	# debug
	# print "nSpots = "+str(nSpots)
	# print "nSpots = "+str(len(SPOTS))

	# read out all tracks definitions
	TRACKS = {}
	line = advanceFileTillLine(f,"Track name")
	while line:
		idx = line.find("TRACK_ID=")
		tID = int(parseOutNumber(line,idx))

		idx = line.find("NUMBER_SPOTS=")
		tLEN = int(parseOutNumber(line,idx))

		# debug
		print "extracting track ID="+str(tID)+", len="+str(tLEN)

		# all edges in this track
		TRACK = {}
		line = f.readline()
		while line and line.find("Edge SPOT_SOURCE_ID") > -1:
			eS = int(parseOutNumber(line))

			idx = line.find("SPOT_TARGET_ID=")
			eT = int(parseOutNumber(line,idx))

			# debug
			# print str(SPOTS[eS][3])+" -> "+str(SPOTS[eT][3])
			# print str(eS)+" -> "+str(eT)

			# now, let's populate data structures to be able to organize the chaos
			# we want for every track to have an time-ordered list of positions/spots
			#
			# edge goes from time tS to tT
			tS = SPOTS[eS][3]
			tT = SPOTS[eT][3]

			# TRACK at timepoint tS should be referring to spot eS
			if tS in TRACK:
				if TRACK[tS] != eS:
					print "CONSISTENCY PROBLEM, trying "+str(eS)+" but occupied with "+str(TRACK[tS])
			else:
				TRACK[tS]=eS

			# TRACK at timepoint tT should be referring to spot eT
			if tT in TRACK:
				if TRACK[tT] != eT:
					print "CONSISTENCY PROBLEM, trying "+str(eT)+" but occupied with "+str(TRACK[tT])
			else:
				TRACK[tT]=eT

			# first time setting the min,maxTime?
			if minTime == -9999:
				minTime = tS
				maxTime = tS
			else:
				# check min,max vs tS
				if tS < minTime:
					minTime = tS
				if tS > maxTime:
					maxTime = tS

			# check min,max vs tT
			if tT < minTime:
				minTime = tT
			if tT > maxTime:
				maxTime = tT

			line = f.readline()

		# save this track
		TRACKS[tID] = TRACK

		# move on to the next track
		line = advanceFileTillLine(f,"Track name")


	f.close()

	# now scan over the range of time points and draw points
	for t in range(minTime,maxTime+1):
		# image to write into...
		img = [[[0 for z in range(xSize)] for y in range(ySize)] for x in range(zSize)]
		print "NEW IMAGE @ time="+str(t)

		# scan all tracks
		for tID in TRACKS:
			TRACK = TRACKS[tID]

			# does it track has the current timepoint?
			if t in TRACK:
				spot = SPOTS[TRACK[t]]
				drawBall(spot[0],spot[1],spot[2],spot[4],tID,img)

		# now write the image onto harddrive...
		# filename:

		# save it actually


main()
