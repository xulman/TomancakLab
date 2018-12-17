from __future__ import print_function

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
# map of all spots extracted from the XML
SPOTS = {}

# map of neighborhood-ships extracted from the XML, unidirectional (from older to newer timepoint)
NEIG = {}

# map of all tracks that will be reconstructed
TRACKS = {}

# a CellTrackingChallenge.org format of tracks.txt
CTCTRACKS = {}

# one root per one tree from the XML
ROOTS = {}

# here's the layout:
#
# [minT,maxT] = readInputXMLfile() populates:
#
# SPOTS[sid] = [sX,sY,sZ,sT,sR]
# NEIG[sidFrom] = [sidTo1,...,sidToN]
# [minT,maxT] is total time span over all saved trees
#
#
# followTrack() then builds:
#
# TRACKS[tid] = TRACK
# TRACK[time] = sid
#
# CTCTRACKS[id][param], where param=0 for ID, 1 for timeStart, 2 for timeEnd, 3 for parentID
#
# sid = spot id, tid = track id


debugTrees = False

def followTrack(root,ID,parent=0,gen=0):
	# this track we gonna populate now
	# time -> spot_ID
	TRACK = {}

	# init the track with its root
	spot = root
	time = SPOTS[spot][3]
	TRACK[time] = spot

	# debug
	print("new track #"+str(ID)+" @ time="+str(time)+" from spot="+str(root))

	# initiate the CTCTRACKS record
	CTCTRACKS[ID]=[ID,time,-10,parent,gen]

	if debugTrees:
		#prefix tree writing
		for q in range(gen):
			print("\t",end='')
		print("|-\t"+str(root)+"\t",end='')

	# follow the track...
	while spot in NEIG and len(NEIG[spot]) == 1:
		# add next spot/track point
		spot = NEIG[spot][0]
		time = SPOTS[spot][3]
		TRACK[time] = spot

		if debugTrees:
			#infix tree writing
			gen += 1
			print(str(spot)+"\t",end='')

	if debugTrees:
		#suffix tree writing
		print()

	# save this track
	TRACKS[ID] = TRACK
	CTCTRACKS[ID][2] = time

	# if we have followers, we do follow
	oldID = ID
	if spot in NEIG:
		for root in NEIG[spot]:
			ID = followTrack(root,ID+1,oldID,gen+1)

	# we report back the last ID used
	return ID


def writeCTCTRACKS(fileName):
	fo = open(fileName,"w")

	for t in CTCTRACKS:
		T = CTCTRACKS[t]
		fo.write(str(T[0])+" "+str(T[1])+" "+str(T[2])+" "+str(T[3])+"\n")

	fo.close()


def readInputXMLfile(filePath):

	# open the input file
	f = open(filePath,"r")

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
		print("extracting tree ID="+str(tID)+", len="+str(tLEN))

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

			# note that SOURCE_ID and TARGET_ID can actually contain
			# both an edge from SOURCE to TARGET and also from TARGET to SOURCE

			# determine their associated time points
			spotTimeS = SPOTS[eS][3]
			spotTimeT = SPOTS[eT][3]

			# assure that eS is the earlier time point
			if spotTimeS > spotTimeT:
				tmp = eT
				eT = eS
				eS = tmp

				tmp = spotTimeT
				spotTimeT = spotTimeS
				spotTimeS = tmp

			# can the earlier of the two spots be a root of this tree?
			if spotTimeS < minTime:
				minTime = spotTimeS
				minSpot = eS

			# interval update...
			minT = spotTimeS if spotTimeS < minT else minT
			maxT = spotTimeT if spotTimeT > maxT else maxT

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
	return [minT,maxT]


#USAGE EXAMPLE#  # --- this parses the data in ---
#USAGE EXAMPLE#  [minT,maxT] = readInputXMLfile(xmlFile.getAbsolutePath())
#USAGE EXAMPLE#  
#USAGE EXAMPLE#  # now, we have a list of roots & we have neighborhood-ships,
#USAGE EXAMPLE#  # let's reconstruct the trees from their roots,
#USAGE EXAMPLE#  # in fact we do a depth-first search...
#USAGE EXAMPLE#  lastID = 0
#USAGE EXAMPLE#  for root in ROOTS:
#USAGE EXAMPLE#  	print("extracted tree ID="+str(root))
#USAGE EXAMPLE#  	lastID = followTrack(ROOTS[root],lastID+1)
#USAGE EXAMPLE#  # --- this parses the data in ---
