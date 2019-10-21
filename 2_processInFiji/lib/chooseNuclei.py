import math
from ij import IJ
from ij import ImagePlus
from ij.process import ColorProcessor
from ij.process import FloatProcessor

from Nucleus import Nucleus

from testPseudoClosing import pseudoClosing
from testPseudoClosing import pseudoDilation

def findComponents(imp,bgPixelValue,realSizes,realCoords,prefix):
	# obtain "handle" to the pixels
	ip = imp.getProcessor()

	# fix pixel values
	valueOnBG = 0 if bgPixelValue == 2 else 255
	valueOnFG = 255 - valueOnBG

	for x in range(imp.getWidth()):
		for y in range(imp.getHeight()):
			if ip.getPixel(x, y) == bgPixelValue:
				ip.set(x,y,valueOnBG)
			else:
				ip.set(x,y,valueOnFG)

	# da frame :)
	for x in range(imp.getWidth()):
		ip.set(x,0,0);
		ip.set(x,1,0);
	for y in range(imp.getHeight()):
		ip.set(0,               y,0);
		ip.set(1,               y,0);
		ip.set(imp.getWidth()-2,y,0);
		ip.set(imp.getWidth()-1,y,0);
	for x in range(imp.getWidth()):
		ip.set(x,imp.getHeight()-2,0);
		ip.set(x,imp.getHeight()-1,0);

	#Detect connected components (aka Nuclei)
	IJ.run("Threshold to label map (2D, 3D)", "threshold=20")
	labelMap = IJ.getImage()
	labelMap.setTitle(prefix+"labelled_image")

	# test and fail iff 'labelMap' contains no components
	if getCurrentMaxPixelValue(labelMap.getProcessor()) == 1:
		print "empty input image detected, returning with no components"
		return []

	pseudoDilation(labelMap)
	labelMap.updateAndRepaintWindow()
	pseudoClosing(labelMap)
	labelMap.updateAndRepaintWindow()

	# restore da frame (pseudoDilation could have damaged it)
	LPP = labelMap.getProcessor()
	for x in range(labelMap.getWidth()):
		LPP.set(x,0,0);
		LPP.set(x,1,0);
	for y in range(labelMap.getHeight()):
		LPP.set(0,               y,0);
		LPP.set(1,               y,0);
		LPP.set(labelMap.getWidth()-2,y,0);
		LPP.set(labelMap.getWidth()-1,y,0);
	for x in range(labelMap.getWidth()):
		LPP.set(x,labelMap.getHeight()-2,0);
		LPP.set(x,labelMap.getHeight()-1,0);

	#Detect all pixels belonging to one Color
	# (builds a list of lists of pixel coords -- pixelPerColor[label][0] = first coordinate
	pixelPerColor = {}
	for x in range(labelMap.width):
		for y in range(labelMap.height):
			MyColor = int(LPP.getf(x,y))
			if MyColor != 0:
				if MyColor in pixelPerColor:
					pixelPerColor[MyColor].append([x,y])
				else:
					#print "detected (1st run): "+str(MyColor)
					pixelPerColor[MyColor] = [[x,y]]

	# a list of detected objects (connected components)
	components = []
	for Color in pixelPerColor:
		components.append(Nucleus(prefix+str(Color),pixelPerColor[Color],LPP,realSizes,realCoords))

	return components


def chooseNuclei(imp,bgPixelValue,realSizes,realCoords, filterArea,areaMin,areaMax, filterCirc,circularityMin,circularityMax):
	return chooseNucleiNew(imp,bgPixelValue,realSizes,realCoords, filterArea,areaMin,areaMax, filterCirc,circularityMin,circularityMax, False)

def chooseNucleiNew(imp,bgPixelValue,realSizes,realCoords, filterArea,areaMin,areaMax, filterCirc,circularityMin,circularityMax, reDetectNuclei):
	# obtain "handle" to the pixels, and impose a bgPixelValue'ed frame at the border of the image
	ip = imp.getProcessor()

	# obtain list of all components that are found initially in the image
	components = findComponents(imp,bgPixelValue,realSizes,realCoords,"1_")

	# reference on the image in the currently active window
	# (which is the 'labelled_image')
	lip = IJ.getImage().getProcessor();

	# output list of nuclei
	nuclei = []
	areThereSomeObjectsLeft = False

	# initiate at first only with nicely passing nuclei
	# and remove pixels from the passing components from the initial/segmentation image
	# (so that pixels from non-passing components will be the only left there)
	for comp in components:
		if comp.doesQualify(filterArea,areaMin,areaMax, filterCirc,circularityMin,circularityMax) == True:
			#enlist
			nuclei.append(comp)
			#erase from input
			for pix in comp.Pixels:
				ip.setf(pix[0],pix[1], 0)
		else:
			#erase from 'labelled_image'
			for pix in comp.Pixels:
				lip.setf(pix[0],pix[1], 0)
			areThereSomeObjectsLeft = True

	# update the 'labelled_image' and the input image (with left-out components)
	IJ.getImage().updateAndRepaintWindow()
	imp.updateAndRepaintWindow()

	if areThereSomeObjectsLeft and reDetectNuclei:
		# bring the input image into forefront... (so that we can work on it)
		IJ.selectWindow(imp.getTitle())

		# NB: the sense of what is BG and FG is switched, hence we start with erosion...
		IJ.run("Erode")
		IJ.run("Erode")
		IJ.run("Erode")
		IJ.run("Dilate")
		IJ.run("Dilate")
		IJ.run("Dilate")

		# find again the new components
		components = findComponents(imp,255,realSizes,realCoords,"2_")

		# and filter again this new components
		for comp in components:
			if comp.doesQualify(filterArea,areaMin,areaMax, filterCirc,circularityMin,circularityMax) == True:
				#enlist
				nuclei.append(comp)

	return nuclei


def drawChosenNuclei(width,height, nuclei):
	# initial colour palette
	colors = [0x00FF00, 0xFFFFFF, 0x0000FF, 0xFF0000]
	colNo = len(colors)

	#initiate output pixel buffer
	OutputPixels = [[0 for y in range(width)] for x in range(height)]

	nuclCnt = 0
	for nucl in nuclei:
		nuclCnt += 1
		color = colors[nuclCnt % colNo]
		for pix in nucl.Pixels:
			OutputPixels[pix[1]][pix[0]] = color

	OutputPixelsNew = reduce(lambda x,y :x+y ,OutputPixels)
	cp = ColorProcessor(width,height, OutputPixelsNew)
	OutputImg = ImagePlus("Choosen Nuclei", cp)
	OutputImg.show()


def drawChosenNucleiValue(width,height, nuclei):
	drawChosenNucleiValue("Visualized Nuclei",width,height, nuclei)

def drawChosenNucleiValue(title, width,height, nuclei):
	# will place Nucleus.DrawValue into the image

	#initiate output pixel buffer
	OutputPixels = [[0.0 for y in range(width)] for x in range(height)]

	for nucl in nuclei:
		for pix in nucl.Pixels:
			OutputPixels[pix[1]][pix[0]] = nucl.DrawValue

	OutputPixelsNew = reduce(lambda x,y :x+y ,OutputPixels)
	cp = FloatProcessor(width,height, OutputPixelsNew)
	OutputImg = ImagePlus(title, cp)
	OutputImg.show()


def drawLine(fromXYtuple, toXYtuple, drawValue,  image,width):
	# find the largest side of a AABB around the requested line
	dx = int(math.fabs( toXYtuple[0] - fromXYtuple[0] ))
	dy = int(math.fabs( toXYtuple[1] - fromXYtuple[1] ))
	iters = max( dx,dy )

	# step:
	dx = (toXYtuple[0] - fromXYtuple[0]) / float(iters)
	dy = (toXYtuple[1] - fromXYtuple[1]) / float(iters)

	for i in range(iters+1):
		x = int(fromXYtuple[0] + float(i)*dx +0.5)
		y = int(fromXYtuple[1] + float(i)*dy +0.5)
		image[ y*width +x ] = drawValue

	# since 'iters' may not be sufficient to reach the line endpoint,
	# we draw the endpoint here explicitly
	image[ int(toXYtuple[1])*width +int(toXYtuple[0]) ] = drawValue


def preprocessMembraneImage(realSizes):
	# obtain "handles"...
	imp = IJ.getImage()
	ip = imp.getProcessor()

	# are there any membrane pixels at all?
	# (aka: avoid troubles when processing an empty image later)
	if getCurrentMaxPixelValue(ip) > 1:
		# remove small components -- which is typically holes inside the nuclei
		IJ.run("3D Objects Counter", "threshold=2 slice=1 min.=20 max.=9999999 objects")
		sizeFilteredImg = IJ.getImage()

		# skeletonize (at the input resolution)
		IJ.setThreshold(0,0)
		IJ.run("Convert to Mask")
		IJ.run("Grays");
		IJ.run("Skeletonize","BlackBackground=false")

		# upscale to the desired resolution, now skeleton gets fatter
		IJ.run("Scale...", "x=- y=- width="+str(len(realSizes))+" height="+str(len(realSizes[0]))+" interpolation=None average create title=upScaledSkeleton.tif");
		upScaledSkeleton = IJ.getImage()

		# close the previous image
		sizeFilteredImg.changes = False
		sizeFilteredImg.close()

		# thin it again (by skeletonizing again)
		IJ.run("Skeletonize","BlackBackground=false")
		# must dilate because "Threshold to label map (2D, 3D)" (which is used
		# in findComponents()) uses 8-neigborhood and would leak through the skeleton
		IJ.run("Dilate")
		# BTW: now the 'upScaledSkeleton' is up-scaled and ready for finding components

		# also up-scale the input image
		IJ.run(imp,"Scale...", "x=- y=- width="+str(len(realSizes))+" height="+str(len(realSizes[0]))+" interpolation=None average create title=upScaledOrigImg.tif");

		# and replace all 'old 2' (upscaled input membranes) with 'new 2' (upscaled skeleton)
		imp = IJ.getImage()
		ip = imp.getProcessor()
		sp = upScaledSkeleton.getProcessor()

		for x in range(imp.getWidth()):
			for y in range(imp.getHeight()):
				if ip.getPixel(x,y) == 2:
					ip.set(x,y,0)
				if sp.getPixel(x,y) == 0:
					ip.set(x,y,2)

		# close also the solo-skeleton image
		upScaledSkeleton.changes = False
		upScaledSkeleton.close()
	else:
		print "empty input image detected, no membrane preprocessing"
		IJ.run(imp,"Scale...", "x=- y=- width="+str(len(realSizes))+" height="+str(len(realSizes[0]))+" interpolation=None average create title=upScaledOrigImg.tif");


def getCurrentMaxPixelValue(ip):
	maxVal = 0
	for i in ip.getPixels():
		maxVal = maxVal if maxVal >= i else i

	return maxVal
