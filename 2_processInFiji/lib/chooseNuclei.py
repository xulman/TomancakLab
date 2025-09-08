from ij import IJ
from ij import ImagePlus
from ij.process import ColorProcessor
from ij.process import FloatProcessor

from Nucleus import Nucleus

def findComponents(imp,bgPixelValue,realSizes,realCoords,prefix):
	# obtain "handle" to the pixels
	ip = imp.getProcessor()

	# fix pixel values
	for x in range(imp.getWidth()):
		for y in range(imp.getHeight()):
			if (ip.getPixel(x, y) == bgPixelValue or ip.getPixel(x, y) == 0):
				ip.set(x,y,0)
			else:
				ip.set(x,y,255)

	#Detect Nuclei
	IJ.run(imp, "HMaxima local maximum detection (2D, 3D)", "minimum=1 threshold=0")
	labelMap = IJ.getImage()
	LPP = labelMap.getProcessor()

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
	labelMap.close()

	# a list of detected objects (connected components)
	components = []
	for Color in pixelPerColor:
		components.append(Nucleus(prefix+str(Color),pixelPerColor[Color],ip,realSizes,realCoords))

	return components


def chooseNuclei(imp,bgPixelValue,realSizes,realCoords, filterArea,areaMin,areaMax, filterCirc,circularityMin,circularityMax):
	# obtain "handle" to the pixels, and impose a bgPixelValue'ed frame at the border of the image
	ip = imp.getProcessor()

	# make sure the image is always visible for this processing
	imp.show()

	# da frame :)
	for x in range(imp.getWidth()):
		ip.set(x,0,bgPixelValue);
		ip.set(x,1,bgPixelValue);
	for y in range(imp.getHeight()):
		ip.set(0,               y,bgPixelValue);
		ip.set(1,               y,bgPixelValue);
		ip.set(imp.getWidth()-2,y,bgPixelValue);
		ip.set(imp.getWidth()-1,y,bgPixelValue);
	for x in range(imp.getWidth()):
		ip.set(x,imp.getHeight()-2,bgPixelValue);
		ip.set(x,imp.getHeight()-1,bgPixelValue);

	# obtain list of all components that are found initially in the image
	components = findComponents(imp,bgPixelValue,realSizes,realCoords,"1_")

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
			areThereSomeObjectsLeft = True

	areThereSomeObjectsLeft = False
	if areThereSomeObjectsLeft:
		# close (and slightly dilate) the original image
		# NB: the sense of what is BG and FG is switched, hence we start with erosion...
		IJ.run("Erode")
		IJ.run("Erode")
		IJ.run("Erode")
		IJ.run("Dilate")
		IJ.run("Dilate")
		IJ.run("Dilate")

		# da frame :)
		for x in range(imp.getWidth()):
			ip.set(x,0,bgPixelValue);
			ip.set(x,1,bgPixelValue);
		for y in range(imp.getHeight()):
			ip.set(0,               y,bgPixelValue);
			ip.set(1,               y,bgPixelValue);
			ip.set(imp.getWidth()-2,y,bgPixelValue);
			ip.set(imp.getWidth()-1,y,bgPixelValue);
		for x in range(imp.getWidth()):
			ip.set(x,imp.getHeight()-2,bgPixelValue);
			ip.set(x,imp.getHeight()-1,bgPixelValue);

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
