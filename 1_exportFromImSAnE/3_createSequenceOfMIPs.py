#@File (style="directory", label="Directory with the stacks") inputDir
#@int (label="First time-point to be used", value="1") timeSpanFrom
#@int (label="Last  time-point to be used", value="2") timeSpanTo
#@String (label="MIP ranges") slicesForMIP
#@boolean (label="Create separate folders for every MIP range") createFolders
#@boolean (label="Create combined stacks over all MIP ranges") createStacks

# This script works on the output of the previous script, that is, it works on a
# sequence of 3D stacks that are to be found in the folder $inputDir. It then
# reads one by one the stacks within the given time point interval and extracts
# Maximum Intensity Projections (MIPs) over the 3rd coordinate (z-axis). There
# will be actually a couple of such projections calculated, each over its interval of
# z-slices (alltogether specified as a comma separated list of ranges: 3-6,8-10),
# and saved into $inputDir in respective folders. The script can also build
# 3D stacks where slices of any stack are the individual MIP images (the stack has
# that many slices how many projections are there per one time point).

# Usage:
# 	- Run Fiji
#	- Run this script
#	- Choose the input folder and ranges

from ij import IJ
import os
import ij.ImagePlus
import ij.ImageStack


def parseOutRangePair(rangeStr):
	i = rangeStr.find('-')
	if (i == -1):
		print "haven't find the range separator '-', returning None instead"
		return None

	q = int(rangeStr[0:i])
	w = int(rangeStr[i+1:len(rangeStr)])
	return [q,w]


def outputMIPfolderPath(r):
	return inputDir.getPath()+"/MIP_z="+str(r[0])+"-"+str(r[1])

def output3DMIPfolderPath():
	return inputDir.getPath() + "/MIP_crippled3D"


def main():
	# output list of range pairs
	ranges=[]

	# currently processed substring is given with q,w
	q=0
	w=slicesForMIP.find(',')
	if (w == -1):
		w=len(slicesForMIP)

	# iterate as long as there are non-empty substrings
	while (q < w):
		r = parseOutRangePair(slicesForMIP[q:w])
		if (r != None):
			ranges.append(r)

		q=w + 1;
		w=q + slicesForMIP[q:len(slicesForMIP)].find(',')
		if (w == q-1):
			w=len(slicesForMIP)

	# some debugging report:
	print "Got this ranges: "+slicesForMIP

	# exclude ranges that make no sense
	ri = 0
	while ri < len(ranges):
		r = ranges[ri]
		if (r[0] > r[1] or r[0] < 1 or r[1] < 1):
			print "Removing range: "+str(r[0])+" - "+str(r[1])
			ranges.remove(r)
			# remove() changed the 'ranges', we better start again...
			ri = 0
		ri+=1

	# some debugging report:
	for r in ranges:
		print "Will use range: "+str(r[0])+" - "+str(r[1])

	if createFolders:
		for r in ranges:
			path = outputMIPfolderPath(r)
			# try to create output folders
			if (os.path.isdir(path) == False):
				os.mkdir(path)

	if createStacks:
		path = output3DMIPfolderPath()
		# try to create output folders
		if (os.path.isdir(path) == False):
			os.mkdir(path)

	# skip the rest of the work if asked to do nothing...
	if (not createFolders and not createStacks):
		return

	# a list of time points
	for TT in range(timeSpanFrom,timeSpanTo+1):
		# a properly formatted string with time point
		T = '%(time)04d' % { 'time' : TT }

		# read the input stack
		F = inputDir.getPath() + "/cmp_3D_T" + T + ".tif"
		img = IJ.openImage(F)
		if (img is None):
			print "couldn't open file: "+F
			return
		img.show()

		# list of MIPed slices to build the output stack (if asked to do so)
		omgs = []

		for r in ranges:
			# check whether sliceTo indices are within the image z-axis range
			if (r[1] > img.getStackSize()):
				print "Some slice TO index is beyond last z-slice."
				img.close()
				return

			# calculate the MIP
			IJ.run("Z Project...", "start="+str(r[0])+" stop="+str(r[1])+" projection=[Max Intensity]");
			omg = IJ.getImage();

			# save individually (if asked to do so)
			if createFolders:
				F = outputMIPfolderPath(r) + "/cmp_MIP_T" + T + ".tif"
				print "saving: "+F
				IJ.save(omg,F)

			if createStacks:
				# hide the MIP image window but remember the image (for later building the stack)
				omg.hide()
				omgs.append(omg)
			else:
				# not needed anymore, close this MIP
				omg.close()

		# build the stack... and close the MIP images (in omgs)
		if createStacks:
			stack = ij.ImageStack(img.getWidth(), img.getHeight())
			for omg in omgs:
				stack.addSlice(omg.getProcessor())
				omg.close()

			# also save the stack image
			F = output3DMIPfolderPath() + "/cmp_MIPs_T" + T + ".tif"
			print "saving: "+F
			IJ.save(ij.ImagePlus(F,stack),F)

		img.close()


main()
