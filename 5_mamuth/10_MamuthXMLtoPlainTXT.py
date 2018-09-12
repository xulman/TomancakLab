from __future__ import print_function
#@File (label="Input Mamuth XML file:") xmlFile
#@File (label="Output plain TXT file:") txtFile
#@String (label="track pairs, e.g. 3-13,22-18") trackPairs

# this section adds a folder, in which this very script is living,
# to the current search paths so that we can import any script living next to this one
import sys.path
import os.path
import inspect
ScriptsRoot = os.path.dirname(os.path.dirname(sys.path[0]))+os.sep+"scripts"
ThisFile    = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(ScriptsRoot+ThisFile+os.sep+"lib")
sys.path.append(ThisFile+os.sep+"lib")
from MamutXMLreader import *


# for processing of trackPairs
def parseOutRangePair(rangeStr):
	i = rangeStr.find('-')
	if (i == -1):
		print("haven't find the range separator '-', returning None instead")
		return None

	q = int(rangeStr[0:i])
	w = int(rangeStr[i+1:len(rangeStr)])
	return [q,w]


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
	print("Detected pairs:")
	for p in PAIRS:
		print(str(p[0])+" <-> "+str(p[1]))


	# --- this parses the data in ---
	# read the input file and populate the data structures
	[minT,maxT] = readInputXMLfile(xmlFile.getAbsolutePath())

	# now, we have a list of roots & we have neighborhood-ships,
	# let's reconstruct the trees from their roots,
	# in fact we do a depth-first search...
	lastID = 0
	for root in ROOTS:
		print("extracted tree ID="+str(root))
		lastID = followTrack(ROOTS[root],lastID+1)
	# --- this parses the data in ---

	print("detected interval of time points ["+str(minT)+","+str(maxT)+"]")


	# print all tracks:
	# open the output file
	fn = txtFile.getAbsolutePath()
	print("Writing file: "+fn)
	fo = open(fn,"w")
	fo.write("# TIME X Y Z TRACK_ID from file "+xmlFile.getAbsolutePath()+"\n")

	for tID in TRACKS.keys():
		# print this track
		# NB: prints TIME, X,Y,Z, TRACK_ID
		TRACK = TRACKS[tID]
		for time in sorted(TRACK.keys()):
			spot = SPOTS[TRACK[time]]
			fo.write( str(time)+"\t"+str(spot[0])+"\t"+str(spot[1])+"\t"+str(spot[2])+"\t"+str(tID)+"\n" )
		fo.write("\n\n")

	fo.close()
	#
	# gnuplot code to display this:
	# splot for [i = 0:2] "embryo6_tub-mamut2.txt" index i u 2:3:4:1 w lp palette pt i+1 t "track ".i


	# print track pairs
	for p in PAIRS:
		# two track IDs from the pair
		q = p[0]
		w = p[1]

		# open output file for writing
		fm = fn[0:len(fn)-4]+"_pair_"+str(q)+"-"+str(w)+fn[len(fn)-4:len(fn)]
		print("Writing file: "+fm)
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
