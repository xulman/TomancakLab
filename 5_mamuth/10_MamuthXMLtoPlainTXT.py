#@File (label="Input Mamuth XML file:") xmlFile
#@File (label="Output plain TXT file:") txtFile
#@String (label="track pairs, e.g. 3-13,22-18") trackPairs


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

# the main work happens here
def main():

	# establish track pairs for the output
	PAIRS=[]

	# currently processed substring is given with q,w
	q=0
	w=trackPairs.find(',')
	if (w == -1):
		w=len(trackPairs)

	# iterate as long as there are non-empty substrings
	while (q < w):
		r = parseOutRangePair(trackPairs[q:w])
		if (r != None):
			PAIRS.append(r)

		q=w + 1;
		w=q + trackPairs[q:len(trackPairs)].find(',')
		if (w == q-1):
			w=len(trackPairs)

	# debug
	# for p in PAIRS:
	# 	print str(p[0])+"<->"+str(p[1])


	# open the output file
	fn = txtFile.getAbsolutePath()
	print "Writing file: "+fn
	fo = open(fn,"w")
	fo.write("# TIME X Y Z TRACK_ID from file "+xmlFile.getAbsolutePath()+"\n")

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
		sT  = parseOutNumber(line,idx)

		# save the currently extracted spot
		SPOTS[sID] = [sX,sY,sZ,sT]


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
					print "CONSISTENCY PROBLEM"
			else:
				TRACK[tS]=eS

			# TRACK at timepoint tT should be referring to spot eT
			if tT in TRACK:
				if TRACK[tT] != eT:
					print "CONSISTENCY PROBLEM"
			else:
				TRACK[tT]=eT

			line = f.readline()

		# save this track
		TRACKS[tID] = TRACK

		# print this track
		# NB: prints TIME, X,Y,Z, TRACK_ID
		for t in sorted(TRACK.keys()):
			spot = SPOTS[TRACK[t]]
			fo.write( str(t)+"\t"+str(spot[0])+"\t"+str(spot[1])+"\t"+str(spot[2])+"\t"+str(tID)+"\n" )
		fo.write("\n\n")
		#
		# gnuplot code to display this:
		# splot for [i = 0:2] "embryo6_tub-mamut2.txt" index i u 2:3:4:1 w lp palette pt i+1 t "track ".i

		# move on to the next track
		line = advanceFileTillLine(f,"Track name")


	f.close()
	fo.close()

	# print track pairs
	for p in PAIRS:
		# two track IDs from the pair
		q = p[0]
		w = p[1]

		# open output file for writing
		fm = fn[0:len(fn)-4]+"_pair_"+str(q)+"-"+str(w)+fn[len(fn)-4:len(fn)]
		print "Writing file: "+fm
		fp = open(fm,"w")
		fp.write("# TIME X Y Z TRACK_ID from file "+xmlFile.getAbsolutePath()+"\n")

		# all timepoints used in both tracks
		qTimes = TRACKS[q].keys()
		wTimes = TRACKS[w].keys()

		# iterate over common timepoints
		for t in sorted(set(qTimes) & set(wTimes)):
			spot = SPOTS[TRACKS[q][t]]
			fp.write( str(t)+"\t"+str(spot[0])+"\t"+str(spot[1])+"\t"+str(spot[2])+"\t"+str(q)+"\t\n" )

			spot = SPOTS[TRACKS[w][t]]
			fp.write( str(t)+"\t"+str(spot[0])+"\t"+str(spot[1])+"\t"+str(spot[2])+"\t"+str(w)+"\t\n\n\n" )

		fp.close()
	#
	# gnuplot code to display this:
	# splot for [i in "14-15 15-16"] "embryo6_tub-mamut2_pair_".i.".txt" u 2:3:4:1 w lp palette t "pair ".i


main()
