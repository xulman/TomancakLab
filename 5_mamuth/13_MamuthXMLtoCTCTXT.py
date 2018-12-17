from __future__ import print_function
#@File (label="Input Mamuth XML file:") xmlFile
#@File (label="Output TXT file:") txtFile
#@boolean (label="Use generation instead of time:") shouldUseGeneration
#@int (label="If generation is used, how long is one:", value=1) oneGenerationDuration

# this section adds a folder, in which this very script is living,
# to the current search paths so that we can import any script living next to this one
import sys.path
import os.path
import inspect
ScriptsRoot = os.path.dirname(os.path.dirname(sys.path[0]))+os.sep+"scripts"
ThisFile    = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.append(ScriptsRoot+os.sep+ThisFile+os.sep+"lib")
sys.path.append(ThisFile+os.sep+"lib")
from MamutXMLreader import *


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

	# save also the CTC tracks.txt if requested so
	fn = txtFile.getAbsolutePath()
	print("Writing file: "+fn)
	if shouldUseGeneration:
		writeGenTRACKS(fn,oneGenerationDuration)
	else:
		writeCTCTRACKS(fn)


main()
