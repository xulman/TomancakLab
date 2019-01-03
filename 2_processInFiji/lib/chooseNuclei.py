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
	countFG = 0
	for x in range(imp.getWidth()):
		for y in range(imp.getHeight()):
			if (ip.getPixel(x, y) == bgPixelValue or ip.getPixel(x, y) == 0):
				ip.set(x,y,255)
			else:
				ip.set(x,y,0)
				countFG = countFG+1

	if countFG == 0:
		print "empty input image detected, returning with no components"
		return []

	# remove small components -- which is typically holes inside the nuclei
	IJ.run("3D Objects Counter", "threshold=128 slice=1 min.=50 max.=9999999 objects")

	# skeletonize!
	IJ.setThreshold(0,0)
	IJ.run("Convert to Mask")
	IJ.run("Grays");
	IJ.run("Skeletonize","BlackBackground=false")
	IJ.run("Dilate")

	# update variables pointing on the currently processed image
	ii = IJ.getImage()
	ip = ii.getProcessor()

	# da frame :)
	for x in range(ii.getWidth()):
		ip.set(x,0,0);
		ip.set(x,1,0);
	for y in range(ii.getHeight()):
		ip.set(0,               y,0);
		ip.set(1,               y,0);
		ip.set(ii.getWidth()-2,y,0);
		ip.set(ii.getWidth()-1,y,0);
	for x in range(ii.getWidth()):
		ip.set(x,ii.getHeight()-2,0);
		ip.set(x,ii.getHeight()-1,0);

	#Detect connected components (aka Nuclei)
	IJ.run("Threshold to label map (2D, 3D)", "threshold=20")
	labelMap = IJ.getImage()
	labelMap.setTitle("labelled_image")

	ii.changes = False
	ii.close()

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

	# leave the connected components map opened
	#labelMap.close()

	# make sure the input image is always visible for further processing
	imp.show()

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

	# make sure the image is always visible for this processing
	imp.show()

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

	# update the 'labelled_image'
	IJ.getImage().updateAndRepaintWindow()

	if areThereSomeObjectsLeft and reDetectNuclei:
		# close the original image
		# NB: the sense of what is BG and FG is switched, hence we start with erosion...
		IJ.run("Erode")
		IJ.run("Erode")
		IJ.run("Erode")
		IJ.run("Dilate")
		IJ.run("Dilate")
		IJ.run("Dilate")

		# find again the new components
		components = findComponents(imp,bgPixelValue,realSizes,realCoords,"2_")

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
