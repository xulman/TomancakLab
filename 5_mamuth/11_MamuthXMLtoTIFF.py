#@File (label="Input Mamuth XML file:") xmlFile
#@File (label="Output folder:") tifFolder
#@int (label="Original image X size:") xSize
#@int (label="Original image Y size:") ySize
#@int (label="Original image Z size:") zSize
#@int (label="Downsampling factor:") xDown

import math

# adjust the size of the output image immediately
Down = float(xDown)
xSize = int(math.ceil(xSize / Down))
ySize = int(math.ceil(ySize / Down))
zSize = int(math.ceil(zSize / Down))


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
	xC = int(math.ceil(xC / Down))
	yC = int(math.ceil(yC / Down))
	zC = int(math.ceil(zC / Down))
	R  = int(math.ceil(R  / Down))

	print "SPOT: "+str(xC)+","+str(yC)+","+str(zC)+" r="+str(R)+" @ ID="+str(Col)

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
					img[x][y][z] = Col


# ------------------------------------------------------------------------------------
# map of all spots extracted from the XML
SPOTS = {}

# map of neighborhood-ships extracted from the XML, unidirectional...
NEIG = {}

# map of all tracks that will be reconstructed
TRACKS = {}


def followTrack(root,ID):
	# this track we gonna populate now
	# time -> spot_ID
	TRACK = {}

	# init the track with its root
	spot = root
	time = SPOTS[spot][3]
	TRACK[time] = spot

	# debug
	print "new track #"+str(ID)+" @ time="+str(time)+" from spot="+str(root)

	# follow the track...
	while spot in NEIG and len(NEIG[spot]) == 1:
		# add next spot/track point
		spot = NEIG[spot][0]
		time = SPOTS[spot][3]
		TRACK[time] = spot

	# save this track
	TRACKS[ID] = TRACK

	# if we have followers, we do follow
	if spot in NEIG:
		for root in NEIG[spot]:
			ID = followTrack(root,ID+1)

	# we report back the last ID used
	return ID


# ------------------------------------------------------------------------------------
# the main work happens here
def main():

	# open the input file
	f = open(xmlFile.getAbsolutePath(),"r")

	# scan the input file until it finds begining of the definitions of spots
	line = advanceFileTillLine(f,"AllSpots nspots=")

	# read out the number of spots
	nSpots = int(parseOutNumber(line))

	# read out all spots definitions
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

	# debug
	# print "nSpots = "+str(nSpots)
	# print "nSpots = "+str(len(SPOTS))

	# one root per one tree from the XML
	ROOTS = {}

	# total time span over all saved trees
	minT =  9999999999999999999
	maxT = -9999999999999999999

	# read out all tracks definitions
	line = advanceFileTillLine(f,"Track name")
	while line:
		idx = line.find("TRACK_ID=")
		tID = int(parseOutNumber(line,idx))

		idx = line.find("NUMBER_SPOTS=")
		tLEN = int(parseOutNumber(line,idx))

		# debug
		print "extracting tree ID="+str(tID)+", len="+str(tLEN)

		minTime = 9999999999999999999
		minSpot = -1

		# all edges in this track
		line = f.readline()
		while line and line.find("Edge SPOT_SOURCE_ID") > -1:
			eS = int(parseOutNumber(line))

			idx = line.find("SPOT_TARGET_ID=")
			eT = int(parseOutNumber(line,idx))

			# debug
			# print str(SPOTS[eS][3])+" -> "+str(SPOTS[eT][3])
			# print str(eS)+" -> "+str(eT)

			# can any of the two spots be a root of this tree?
			# NB: theoretically we should consider only eS...
			spotTime = SPOTS[eS][3]
			if spotTime < minTime:
				minTime = spotTime
				minSpot = eS

			# interval update...
			minT = spotTime if spotTime < minT else minT
			maxT = spotTime if spotTime > maxT else maxT

			spotTime = SPOTS[eT][3]
			if spotTime < minTime:
				minTime = spotTime
				minSpot = eT

			# interval update...
			minT = spotTime if spotTime < minT else minT
			maxT = spotTime if spotTime > maxT else maxT

			# store the edge, which goes from spot eS to eT
			if eS in NEIG:
				NEIG[eS].append(eT)
			else:
				NEIG[eS] = [eT]

			line = f.readline()

		# this track/tree is finished
		ROOTS[tID] = minSpot;

		# move on to the next track
		line = advanceFileTillLine(f,"Track name")

	f.close()

	# now, we have a list of roots & we have neighborhood-ships,
	# let's reconstruct the trees from their roots,
	# in fact we do a depth-first search...
	lastID = 0
	for root in ROOTS:
		print "extracted tree ID="+str(root)
		lastID = followTrack(ROOTS[root],lastID+1)

	# create the output image (only once cause it is slow)
	img = [[[0 for z in range(zSize)] for y in range(ySize)] for x in range(xSize)]

	# now scan over the range of time points and draw points
	for t in range(minT,maxT+1):
		# filename:
		fn = tifFolder.getAbsolutePath()+"/time{0:03d}.tif".format(t)
		print "Writing file: "+fn

		# prepare the output image
		for x in range(xSize):
			for y in range(ySize):
				for z in range(zSize):
					img[x][y][z] = 0

		# scan all tracks
		for tID in TRACKS:
			TRACK = TRACKS[tID]

			# does this track has the current timepoint?
			if t in TRACK:
				spot = SPOTS[TRACK[t]]
				drawBall(spot[0],spot[1],spot[2],spot[4],tID,img)

		# now write the image onto harddrive...


main()
