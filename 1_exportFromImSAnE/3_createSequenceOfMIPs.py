#@File (style="directory", label="Directory with the stacks") inputDir
#@int (label="First time-point to be used", value="1") timeSpanFrom
#@int (label="Last  time-point to be used", value="2") timeSpanTo
#@int (label="MIP A: z-slice FROM", value="0") AsliceFrom
#@int (label="MIP A: z-slice   TO", value="1") AsliceTo
#@int (label="MIP B: z-slice FROM", value="0") BsliceFrom
#@int (label="MIP B: z-slice   TO", value="1") BsliceTo

# This script works on the output of the previous script, that is it works on a
# sequence of 3D stacks that are to be found in the folder $inputDir. It then
# reads one by one the stacks withint the given time point interval and extracts
# Maximum Intensity Projections (MIPs) over the 3rd coordinate (z-axis). There
# will be actually two such projections calculated, each over its interval of
# z-slices, and saved into $inputDir/MIP_A and $inputDir/MIP_B, respectively.

# Usage:
# 	- Run Fiji
#	- Run this script
#	- Choose the input folder and ranges

from ij import IJ
import os
import ij.ImagePlus
import ij.ImageStack


def main():
	# try to create output folders
	if (os.path.isdir(inputDir.getPath() + "/MIP_A") == False):
		os.mkdir(inputDir.getPath() + "/MIP_A")

	if (os.path.isdir(inputDir.getPath() + "/MIP_B") == False):
		os.mkdir(inputDir.getPath() + "/MIP_B")

	# check that input z-ranges make sense
	if (AsliceFrom < 1 or BsliceFrom < 1):
		print "A or B slice FROM index can't be less than 1."
		return
	if (AsliceFrom > AsliceTo or BsliceFrom > BsliceTo):
		print "A or B slice FROM index can't be larger than TO index."
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

		# check whether A/BsliceTo indices are within the image z-axis range
		if (AsliceTo > img.getStackSize() or BsliceTo > img.getStackSize()):
			print "A or B slice TO index is beyond last z-slice."
			return

		# 1st interval
		# start with the first projected plane...
		# and create an initial MIP from it
		F = inputDir.getPath() + "/MIP_A/cmp_MIP_T" + T + ".tif"
		img.setZ(AsliceFrom)
		omg = ij.ImagePlus(F,img.getProcessor().duplicate())
		op = omg.getProcessor()

		# do the projection over the first range of slices
		for Z in range(AsliceFrom+1, AsliceTo+1):
			img.setZ(Z)
			ip = img.getProcessor();

			# one slice "merging"
			for y in range(ip.height):
				for x in range(ip.width):
					valI = ip.getf(x,y)
					valO = op.getf(x,y)
					if (valI > valO):
						op.setf(x,y,valI)

		# now, create and save the image
		print "saving: "+F
		IJ.save(omg,F)


		# 2nd interval
		# start with the first projected plane...
		# and create an initial MIP from it
		F = inputDir.getPath() + "/MIP_B/cmp_MIP_T" + T + ".tif"
		img.setZ(BsliceFrom)
		omg = ij.ImagePlus(F,img.getProcessor().duplicate())
		op = omg.getProcessor()

		# do the projection over the first range of slices
		for Z in range(BsliceFrom+1, BsliceTo+1):
			img.setZ(Z)
			ip = img.getProcessor();

			# one slice "merging"
			for y in range(ip.height):
				for x in range(ip.width):
					valI = ip.getf(x,y)
					valO = op.getf(x,y)
					if (valI > valO):
						op.setf(x,y,valI)

		# now, create and save the image
		print "saving: "+F
		IJ.save(omg,F)


main()
