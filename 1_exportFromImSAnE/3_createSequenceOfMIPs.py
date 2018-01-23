#@File (style="directory", label="Directory with the stacks") inputDir
#@int (label="First time-point to be used", value="1") timeSpanFrom
#@int (label="Last  time-point to be used", value="2") timeSpanTo
#@int (label="MIP A: z-slice FROM", value="0") AsliceFrom
#@int (label="MIP A: z-slice   TO", value="1") AsliceTo
#@int (label="MIP B: z-slice FROM", value="0") BsliceFrom
#@int (label="MIP B: z-slice   TO", value="1") BsliceTo
#@int (label="MIP C: z-slice FROM", value="0") CsliceFrom
#@int (label="MIP C: z-slice   TO", value="1") CsliceTo
#@int (label="MIP D: z-slice FROM", value="0") DsliceFrom
#@int (label="MIP D: z-slice   TO", value="1") DsliceTo

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

	if (os.path.isdir(inputDir.getPath() + "/MIP_C") == False):
		os.mkdir(inputDir.getPath() + "/MIP_C")

	if (os.path.isdir(inputDir.getPath() + "/MIP_D") == False):
		os.mkdir(inputDir.getPath() + "/MIP_D")

	# check that input z-ranges make sense
	if (AsliceFrom < 1 or BsliceFrom < 1 or CsliceFrom < 1 or DsliceFrom < 1):
		print "Some slice FROM index can't be less than 1."
		return
	if (AsliceFrom > AsliceTo or BsliceFrom > BsliceTo or CsliceFrom > CsliceTo or DsliceFrom > DsliceTo):
		print "Some slice FROM index can't be larger than TO index."
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

		# check whether A/BsliceTo indices are within the image z-axis range
		if (AsliceTo > img.getStackSize() or BsliceTo > img.getStackSize() or CsliceTo > img.getStackSize() or DsliceTo > img.getStackSize()):
			print "Some slice TO index is beyond last z-slice."
			return

		# 1st interval
		IJ.run("Z Project...", "start="+str(AsliceFrom)+" stop="+str(AsliceTo)+" projection=[Max Intensity]");
		omg = IJ.getImage();
		F = inputDir.getPath() + "/MIP_A/cmp_MIP_T" + T + ".tif"
		print "saving: "+F
		IJ.save(omg,F)
		omg.close()

		# 2nd interval
		IJ.run("Z Project...", "start="+str(BsliceFrom)+" stop="+str(BsliceTo)+" projection=[Max Intensity]");
		omg = IJ.getImage();
		F = inputDir.getPath() + "/MIP_B/cmp_MIP_T" + T + ".tif"
		print "saving: "+F
		IJ.save(omg,F)
		omg.close()

		# 3rd interval
		IJ.run("Z Project...", "start="+str(CsliceFrom)+" stop="+str(CsliceTo)+" projection=[Max Intensity]");
		omg = IJ.getImage();
		F = inputDir.getPath() + "/MIP_C/cmp_MIP_T" + T + ".tif"
		print "saving: "+F
		IJ.save(omg,F)
		omg.close()

		# 4th interval
		IJ.run("Z Project...", "start="+str(DsliceFrom)+" stop="+str(DsliceTo)+" projection=[Max Intensity]");
		omg = IJ.getImage();
		F = inputDir.getPath() + "/MIP_D/cmp_MIP_T" + T + ".tif"
		print "saving: "+F
		IJ.save(omg,F)
		omg.close()

		img.close()


main()
