#@File (style="directory", label="Input directory with the M layers") inputDirFrom
#@File (style="directory", label="Input directory with the P layers") inputDirTo
#@String (label="path between input dirs and slice images", value="cylinder1_index/cylinder1") subPath
#@File (style="directory", label="Output directory to store stacks") outputDir
#@int (label="First time-point to be used", value="1") timeSpanFrom
#@int (label="Last  time-point to be used", value="2") timeSpanTo

# Consider folder holding multiple folders 'data_layer_m*' and 'data_layer_p*',
# each having (somewhere deep inside in nested folders) a time-lapse sequence
# of 2D images. The user is assumed to choose two such 'data_layer_*' folders
# and this script will iterate between them considering every single one as a
# z-slice of some future stack. But since inside them are time-lapse sequences
# of images, the output is also a time-lapse sequence of stacks of these images:
# for every time point T take every folder F from the respective 'data_layer_*'
# folders and create a stack from slices/images "$F/$subPath/cmp_1_1_T$T.tif"

# Usage:
# 	- Run Fiji
#	- Run this script
#	- Choose the input folders and ranges
#	- Choose an output folder

from ij import IJ
import ij.ImagePlus
import ij.ImageStack


def main():
	# create a list of folders F:
	# extract [pm][:digit:] pattern to determine indices
	# FROM FOLDER
	s = inputDirFrom.getPath()
	i = s.rfind("data_layer_")
	if (i == -1):
		print "haven't find 'data_layer_' in the path of inputDirFrom"
		return

	pat = s[i+11]
	if (i+12 < len(s)):
		pat += s[i+12]
	if (i+13 < len(s)):
		pat += s[i+13]
	pat += '/'

	orderDict = ["m50/","m49/","m48/","m47/","m46/","m45/","m44/","m43/","m42/","m41/","m40/","m39/","m38/","m37/","m36/","m35/","m34/","m33/","m32/","m31/","m30/","m29/","m28/","m27/","m26/","m25/","m24/","m23/","m22/","m21/","m20/","m19/","m18/","m17/","m16/","m15/","m14/","m13/","m12/","m11/","m10/","m9/","m8/","m7/","m6/","m5/","m4/","m3/","m2/","m1/","0/","p1/","p2/","p3/","p4/","p5/","p6/","p7/","p8/","p9/","p10/","p11/","p12/","p13/","p14/","p15/","p16/","p17/","p18/","p19/","p20/","p21/","p22/","p23/","p24/","p25/","p26/","p27/","p28/","p29/","p30/","p31/","p32/","p33/","p34/","p35/","p36/","p37/","p38/","p39/","p40/","p41/","p42/","p43/","p44/","p45/","p46/","p47/","p48/","p49/","p50/"]

	zFrom = -1
	for i in range(len(orderDict)):
		if (orderDict[i].find(pat) > -1):
			#print "Matching pattern "+pat+" against "+orderDict[i]+" (i="+str(i)+")"
			zFrom = i;

	if (zFrom == -1):
		print "haven't recognized '"+pat+"' in the path of inputDirFrom"
		return

	# TO FOLDER
	s = inputDirTo.getPath()
	i = s.rfind("data_layer_")
	if (i == -1):
		print "haven't find 'data_layer_' in the path of inputDirTo"
		return

	pat = s[i+11]
	if (i+12 < len(s)):
		pat += s[i+12]
	if (i+13 < len(s)):
		pat += s[i+13]
	pat += '/'

	zTo = -1
	for ii in range(len(orderDict)):
		if (orderDict[ii].find(pat) > -1):
			#print "Matching pattern "+pat+" against "+orderDict[ii]+" (ii="+str(ii)+")"
			zTo = ii;

	if (zTo == -1):
		print "haven't recognized '"+pat+"' in the path of inputDirTo"
		return

	print "Recognized z interval from "+orderDict[zFrom]+" to "+orderDict[zTo]

	# creates full filenames of the individual input images
	def createInputName(T, FF):
		# s is the string of the inputDirTo
		if (orderDict[FF][0] == '0'):
			F = s[0:i+4] + '/' + subPath + "/cmp_1_1_T" + T + ".tif"
		else:
			F = s[0:i+11] + orderDict[FF] + subPath + "/cmp_1_1_T" + T + ".tif"
		return F


	# a list of time points
	for TT in range(timeSpanFrom,timeSpanTo+1):
		# a properly formatted string with time point
		T = '%(time)04d' % { 'time' : TT }

		# create an empty stack
		# read the first image to determine dimension
		F = createInputName(T,zFrom)
		img = IJ.openImage(F)
		if (img is None):
			print "couldn't open file: "+F
			return

		stack = ij.ImageStack(img.getWidth(), img.getHeight()) #, timeSpanTo-timeSpanFrom+1)
		stack.addSlice(img.getProcessor())
		img.close()

		for FF in range(zFrom+1,zTo+1):
			# a list of folders
			# read slice image and add it
			F = createInputName(T,FF)
			img = IJ.openImage(F)
			if (img is None):
				print "couldn't open file: "+F
				return

			stack.addSlice(img.getProcessor())
			img.close()


		# determine output filename and "report progress bar"
		F = outputDir.getPath() + "/cmp_3D_T" + T + ".tif"
		print "saving: "+F

		# save the created stack image
		IJ.save(ij.ImagePlus(F,stack),F)


main()
