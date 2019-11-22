#@File (label="File with input directories:") inFile
#@int (label="Span of examined channels:", default="4") maxChannel
#@int (label="Span of examined positions:", default="4") maxPosition
#@int (label="Span of examined time points:", default="1000") maxTime
#@int (label="Span of examined z-slices:", default="1000") maxZ

#@File (style="directory", label="Output directory to place the symlinks:") outDir
#@int (label="Time shift:", default="0") timeShift

#@float (label="Voxel width (length along x-axis):") xRes
#@float (label="Voxel height (length along y-axis):") yRes
#@float (label="Voxel depth (length along z-axis):") zRes

#@boolean (label="Rectangular crop:") cropFlag
#@String (label="Rectangular crop box (e.g. 10,10,90,90):", description="This field is required only when the Rectangular crop is checked.") cropString

filePattern =   "img_channel{:03d}_position{:03d}_time{:09d}_z{:03d}.tif"
reportPattern = "img_channel{:03d}_position{:03d}_time{:09d}"

fileOutputPattern =    "spim_TL{}_Angle{}_Position{}.tif"
fileOutputPatternMIP = "spim_TL{}_Angle{}_Position{}_MIP.tif"


import os.path
from ij import IJ
import ij.ImagePlus
import ij.ImageStack

inDirStr = os.path.dirname(inFile.getAbsolutePath())+os.path.sep
outDirStr = outDir.getAbsolutePath()+os.path.sep

outMIPDirStr = outDirStr+"MIP"+os.path.sep
if(not os.path.isdir(outMIPDirStr)):
	os.makedirs(outMIPDirStr)


def fileName(Folder, c,p,t,z):
	return (inDirStr+Folder+os.path.sep+"Default"+os.path.sep+filePattern).format(c,p,t,z)

logger = open(outDirStr+"MapBack.txt","w")


if cropFlag == True:
	cropValues = cropString.split(",")
	cropXfrom = int(cropValues[0])
	cropYfrom = int(cropValues[1])
	cropXtill = int(cropValues[2])
	cropYtill = int(cropValues[3])
	print("Detected crop box: "+str(cropXfrom)+","+str(cropYfrom)+","+str(cropXtill)+","+str(cropYtill))
else:
	print("No cropping.")


def processFolder(Folder):
	global timeShift
	global logger

	# test if the channel 0 exists at all
	img = fileName(Folder, 0,0,0,0)
	if not os.path.exists(img):
		print("Missing the first image: "+img)
		return

	lastAvailChnnl = 1
	while os.path.exists(fileName(Folder, lastAvailChnnl,0,0,0)) and lastAvailChnnl < maxChannel:
		lastAvailChnnl = lastAvailChnnl+1
	lastAvailChnnl = lastAvailChnnl-1

	lastAvailPos = 1
	while os.path.exists(fileName(Folder, 0,lastAvailPos,0,0)) and lastAvailPos < maxPosition:
		lastAvailPos = lastAvailPos+1
	lastAvailPos = lastAvailPos-1

	lastAvailTime = 1
	while os.path.exists(fileName(Folder, 0,0,lastAvailTime,0)) and lastAvailTime < maxTime:
		lastAvailTime = lastAvailTime+1
	lastAvailTime = lastAvailTime-1

	lastAvailZ = 1
	while os.path.exists(fileName(Folder, 0,0,0,lastAvailZ)) and lastAvailZ < maxZ:
		lastAvailZ = lastAvailZ+1
	lastAvailZ = lastAvailZ-1

	print("For the folder "+inDirStr+Folder)
	print("I think the ranges are as follows:")
	print(" Channels: 0 - "+str(lastAvailChnnl))
	print("Positions: 0 - "+str(lastAvailPos))
	print("     Time: 0 - "+str(lastAvailTime))
	print(" Z slices: 0 - "+str(lastAvailZ))

	for t in range(lastAvailTime+1):
		for c in range(lastAvailChnnl+1):
			for p in range(lastAvailPos+1):
				#
				# open the first zSlice image, we're gonna add slices to it and re-save it
				imgFinal = IJ.openImage(fileName(Folder, c,p,t,0))
				if (imgFinal is None):
					print "couldn't open file: "+fileName(Folder, c,p,t,0)
					return

				# get handle on its stack (we'll be adding slices to it)
				#imgStack = imgFinal.getStack()
				imgStack = ij.ImageStack(imgFinal.getWidth(), imgFinal.getHeight())
				imgStack.addSlice( imgFinal.getProcessor() )
				imgFinal.close()

				for z in range(1,lastAvailZ+1):
					#
					# open the next zSlice image
					imgSlice = IJ.openImage(fileName(Folder, c,p,t,z))
					if (imgSlice is None):
						print "couldn't open file: "+fileName(Folder, c,p,t,0)
						return

					# add this slice to the output image
					imgStack.addSlice( imgSlice.getProcessor() )
					imgSlice.close()

				# finally, save the output image
				outFileName = outDirStr+fileOutputPattern.format(timeShift,c,p)
				print("saving image: "+outFileName)

				imgFinal = ij.ImagePlus(outFileName,imgStack)
				IJ.run(imgFinal,"Properties...","unit=um pixel_width="+str(xRes)+" pixel_height="+str(yRes)+" voxel_depth="+str(zRes))
				if cropFlag == True:
					imgFinal.show()
					IJ.makeRectangle( cropXfrom,cropYfrom, cropXtill,cropYtill )
					IJ.run("Crop")

				IJ.save(imgFinal,outFileName)

				IJ.run(imgFinal,"Z Project...","projection=[Max Intensity]")
				MIPimg = IJ.getImage();
				IJ.save(MIPimg,outMIPDirStr+fileOutputPatternMIP.format(timeShift,c,p))
				MIPimg.close()

				if cropFlag == True:
					imgFinal.close()

				logger.write(fileOutputPattern.format(timeShift,c,p)+" = "+(inDirStr+Folder+os.path.sep+"Default"+os.path.sep+reportPattern).format(c,p,t)+"\n")
				logger.flush()


		timeShift = timeShift+1

	print("Done.")




# this loops through the text file that list folder with images
folders = open(inFile.getAbsolutePath(), "r")

for folder in folders:
	initialTimePoint = timeShift
	processFolder( folder.rstrip() )
	#logger.write(folder.rstrip()+"  "+str(initialTimePoint)+"  "+str(timeShift-1)+"\n")
	#logger.flush()

folders.close()
logger.close()
