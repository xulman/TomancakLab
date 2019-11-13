#@int(label="A nucleus is everything  BIGGER than (um^2)") areaMin
#@int(label="A nucleus is everything SMALLER than (um^2)") areaMax
#@boolean (label="Filter according to area") filterArea
#
#@float(label="A nucleus has a circularity  BIGGER than (1 represents perfect circularity)") circularityMin
#@float(label="A nucleus has a circularity SMALLER than (1 represents perfect circularity)") circularityMax
#@boolean (label="Filter according to circularity") filterCirc
#
#-------disabled-------@boolean (label="Input image shows nuclei (checked) or membranes (unchecked)") inputImageShowsNuclei
#-------disabled-------@boolean (label="Nuclei detection: After 1st run, close left-out nuclei and re-run detection", value=False) postprocessNucleiImageFlag
#-------disabled-------@boolean (label="Membrane thinning: Input image should be up-scaled and membranes thinned", value=False) preprocessMembraneImageFlag
inputImageShowsNuclei = False
postprocessNucleiImageFlag = False
preprocessMembraneImageFlag = True

#
#@boolean (label="Polygon boundary straightening:", value=False) polyAsLargeSegments
#-------disabled-------@boolean (label="Polygon boundary smoothing: should do", value=False) polySmoothDo
#-------disabled-------@int     (label="Polygon boundary smoothing: smooth span in half-pixel units", value=10) polySmoothSpan
#-------disabled-------@float   (label="Polygon boundary smoothing: smooth sigma in half-pixel units", value=4) polySmoothSigma
polySmoothDo = False
polySmoothSpan = 10
polySmoothSigma = 4
#
#@File (style="directory", label="Folder with maps:") mapFolder
#@String (label="\"cylinder1\" vs. \"cylinder2\":", value="cylinder1") mapCylinder
class SimpleFile:
	def __init__(self,path):
		self.path = path
	def getAbsolutePath(self):
		return self.path

aMapFile = 0
xMapFile = 0
yMapFile = 0
zMapFile = 0

def prepareMapFilePaths(rootPath):
	global aMapFile
	global xMapFile
	global yMapFile
	global zMapFile
	aMapFile = SimpleFile(rootPath+"/"+mapCylinder+"_area.txt")
	xMapFile = SimpleFile(rootPath+"/"+mapCylinder+"coords_X.txt")
	yMapFile = SimpleFile(rootPath+"/"+mapCylinder+"coords_Y.txt")
	zMapFile = SimpleFile(rootPath+"/"+mapCylinder+"coords_Z.txt")

prepareMapFilePaths( mapFolder.getAbsolutePath() )

#
#@boolean (label="Triangle method (only on straightened polygons):", value=False) doTriangleMethod
#@int (label="Triangle method - centre X for distances in scatter plot (px):") tCentreX
#@int (label="Triangle method - centre Y for distances in scatter plot (px):") tCentreY

#
#@boolean (label="Show sheet with analysis data", value=True) showRawData
#@boolean (label="Show image with areas") showAreaImage
#@boolean (label="Show image with circularities") showCircImage
#@boolean (label="Show image with shape factors") showShapeFactorImage
#@boolean (label="Show image with neighbor counts") showNeigImage

#@boolean (label="Triangle method - paranoid (debug) checks:", value=False) doTriangleMethodParanoid

# This script should be used to find suitable parameters for CountBigNucleiCorrected.py
# You'll see nuclei of various colors:
# green - fit both conditions      (area good, circularity good)
# white - does not fit circularity (area good, circularity bad)
# blue - does not fit area         (area bad,  circularity good)
# red - fails both conditions      (area bad,  circularity bad)
colors = [0x00FF00, 0xFFFFFF, 0x0000FF, 0xFF0000]

# Usage:
#	- Run Fiji
# 	- Make sure that the update site SCF-MPI-CBG is activated
#	- Open one representative image of your data
#	- Run this script
# 	- If you are not confident with the output, repeat with other parameters.

from ij import IJ
from ij import ImagePlus
from ij.process import ColorProcessor
from ij.process import FloatProcessor
from ij.measure import ResultsTable

# this section adds a folder, in which this very script is living,
# to the current search paths so that we can import our "library script"
import sys.path
import os.path
import inspect
ScriptsRoot = os.path.dirname(os.path.dirname(sys.path[0]))+os.sep+"scripts"
ThisFile    = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.append(ScriptsRoot+os.sep+ThisFile+os.sep+"lib")
sys.path.append(ThisFile+os.sep+"lib")

# import our "library scripts"
from importsFromImSAnE import *
from chooseNuclei import *
from properMeasurements import *

# import the same Nucleus class to make sure the very same calculations are used
from Nucleus import Nucleus

# VLADO PROPER CIRC DEBUG
# VLADO PIXEL CIRC DEBUG
import math


# this is the theoretical border line to determine between solid-state
# and fluid-state of a cell based on its shapeFactor value (by comparing
# the shapeFactor with the value of p - given by pCurveOfQ)
def pCurveOfQ(Q):
	return 3.94 + 4 * 0.43 * Q*Q

# content of the future file that contains scatter plot data w.r.t. triangle method
scatterData = []

def main():
	print("wait until \"Done.\" (or error) appears...")
	originalImageName = IJ.getImage().getTitle()

	# FIX: we now assume membrane image to come; in this case, however, the script
	# assumes that membranes pixels store value of 2.0... but the current data use
	# value of 1.0 and so we have to fix it.....
	removeMeImg = IJ.getImage().duplicate()
	removeMeImg.show()
	IJ.run("Add...", "value=1");

	# reads the area_per_pixel information, already in squared microns
	realSizes = readRealSizes(aMapFile.getAbsolutePath())

	# read the 'real Coordinates', that take into account the different pixel sizes
	realCoordinates = readRealCoords(xMapFile.getAbsolutePath(),yMapFile.getAbsolutePath(),zMapFile.getAbsolutePath())

	backgroundPixelValue = 1 # in case of cell nuclei
	if (not inputImageShowsNuclei):
		backgroundPixelValue = 2 # in case of cell membranes
		if preprocessMembraneImageFlag == True:
			print("initial membrane preprocessing...")
			preprocessMembraneImage(realSizes)

	imp = IJ.getImage()

	# test that sizes of realSizes and imp matches
	checkSize2DarrayVsImgPlus(realSizes, imp)
	checkSize2DarrayVsImgPlus(realCoordinates, imp)

	print("extracting individual nuclei and their parameters...")
	# obtain list of all valid nuclei
	nuclei = chooseNucleiNew(imp,backgroundPixelValue,realSizes,realCoordinates, filterArea,areaMin,areaMax, filterCirc,circularityMin,circularityMax, postprocessNucleiImageFlag)
	# add list of all INvalid nuclei (since only invalid are left in the input image)
	#nuclei += findComponents(imp,255,realSizes,realCoordinates,"n_")

	# ------- analysis starts here -------
	if len(nuclei) == 0:
		print("No components found, quiting...")
		return

	circularitySum = 0
	shapeFactorSum = 0
	sizeSum = 0

	i = IJ.getImage().getProcessor().getPixels()
	w = IJ.getImage().getWidth()

	if polyAsLargeSegments == True:
		print("redesigning nuclei boundaries - fitting line segments...")
	if polySmoothDo == True:
		print("redesigning nuclei boundaries - smoothing it out...")
	if polyAsLargeSegments == True or polySmoothDo == True:
		print("recalculating nuclei parameters since boundaries have changed...")
	if (not inputImageShowsNuclei):
		print("calculating number of neighbors per cell...")

	drasticAreaChange = 0
	for nucl in nuclei:
		# should straightening happen?
		if polyAsLargeSegments == True:
			nucl.reshapeNucleusWithStraightenedBoundary(i,w)

		if polySmoothDo == True:
			nucl.smoothPolygonBoundary(polySmoothSpan,polySmoothSigma)

		if polyAsLargeSegments == True or polySmoothDo == True:
			# update everything that depends on a corrected area and perimeter length
			nucl.EdgeLength = properLength(nucl.Coords,realCoordinates)
			origArea = nucl.Area
			nucl.getBoundaryInducedArea(realSizes)
			nucl.updateCircularityAndSA()

			if nucl.Area/origArea < 0.90 or nucl.Area/origArea > 1.10:
				drasticAreaChange = drasticAreaChange+1

		circularitySum += nucl.Circularity
		shapeFactorSum += nucl.ShapeFactor
		sizeSum += nucl.Area
		if (not inputImageShowsNuclei):
			nucl.setNeighborsList(i,w)


	if polyAsLargeSegments == True and drasticAreaChange > 0:
		print("WARNING: "+str(drasticAreaChange)+"/"+str(len(nuclei))
		     +" cells have real area change larger than 10%.")

	print("Average Circularity: "+str(circularitySum/len(nuclei)))
	print("Average ShapeFactor: "+str(shapeFactorSum/len(nuclei)))
	print("Average Area: "+str(sizeSum/len(nuclei))+" square microns")

	if inputImageShowsNuclei:
		print("No. of neighborhood was not counted, works only with membrane images.")

	if polyAsLargeSegments == True:
		# remove nuclei near vertical border
		mustStay = []
		for nucl in nuclei:
			if nucl.CentreX > 50 and nucl.CentreX < 1650:
				mustStay.append(nucl)

		nuclei = mustStay

	if polyAsLargeSegments == True or polySmoothDo == True:
		for nucl in nuclei:
			nucl.DrawValue = nucl.Label
		drawChosenNucleiValue(originalImageName+": NEW SHAPES", imp.getWidth(),imp.getHeight(), nuclei)
		# the 'i' variable must be "re-directed" to pixel array that is showing the current shapes of nuclei
		i = IJ.getImage().getProcessor().getPixels()

	if showCircImage:
		for nucl in nuclei:
			nucl.DrawValue = nucl.Circularity
		drawChosenNucleiValue(originalImageName+": Real circularities", imp.getWidth(),imp.getHeight(), nuclei)

	if showShapeFactorImage:
		for nucl in nuclei:
			nucl.DrawValue = nucl.ShapeFactor
		drawChosenNucleiValue(originalImageName+": Real shape factors", imp.getWidth(),imp.getHeight(), nuclei)

	if showAreaImage:
		for nucl in nuclei:
			nucl.DrawValue = nucl.Area;
		drawChosenNucleiValue(originalImageName+": Real areas", imp.getWidth(),imp.getHeight(), nuclei)

	if showNeigImage:
		for nucl in nuclei:
			nucl.DrawValue = len(nucl.NeighIDs);
		drawChosenNucleiValue(originalImageName+": Neighborhood counts", imp.getWidth(),imp.getHeight(), nuclei)


	if doTriangleMethod == True:
		if polyAsLargeSegments == True:
			print("Calculating the cell alignment parameter (the triangle method).")

			# every nucleus lists all junction points relevant to it, the neighboring
			# nuclei must be sharing them, we have to "invert this" to maintain a list
			# of triangles adjacent (giving rise) to any junction point
			vertices = []

			# the "2px radius" pattern
			jn = [ -2*w-2, -2*w-1, -2*w, -2*w+1, -2*w+2,
			       -1*w-2,                       -1*w+2,
			        -2,                           +2,
			       +1*w-2,                       +1*w+2,
			       +2*w-2, +2*w-1, +2*w, +2*w+1, +2*w+2 ]

			# also, build a map nucl.Label to nuclei object (to build triangles faster)
			nucleiMap = {}

			# DEBUG
			verticesVizu = []

			for nucl in nuclei:
				nucleiMap[nucl.Label] = nucl

				for jp in nucl.CoordsInnerJunctions:
					visitedLabels = set()
					for dp in jn:
						if jp+dp >= 0 and jp+dp < len(i) and i[jp+dp] > 0:
							visitedLabels.add( i[jp+dp] )

					# if a junction point that is surrounded by at least three
					# labels (nuclei/cells) is found, we'll enlist it if it has
					# not been enlisted already
					if len(visitedLabels) >= 3:
						found = False
						for t in vertices:
							if visitedLabels <= t:
								found = True
								break

						if found == False:
							vertices.append(visitedLabels)
							# DEBUG
							verticesVizu.append(jp)

			print("  Discovered vertices cnt: "+str(len(vertices)))

			# due to the processing order of the vertices, it may happen that A, A is subset of B
			# and should not therefore be included, was inserted before the B:
			# (and since removing from the list is expensive/impossible we have an "ignore list")
			verticesIgnoredIdxs = []
			for v in vertices:
				if len(v) > 3:
					for i in range(len(vertices)):
						if vertices[i] < v:
							verticesIgnoredIdxs.append(i)

			print("  Discovered duplicate vertices cnt: "+str(len(verticesIgnoredIdxs)))

			print("  Rendering vertices as crosses to be checked against the NEW SHAPES image...")
			# render all vertices
			imgHeight = IJ.getImage().getHeight()
			vPixels = [0 for o in range(w * imgHeight)]
			for v in verticesVizu:
				vPixels[v] = vPixels[v]+1
			for i in verticesIgnoredIdxs:
				vPixels[ verticesVizu[i] ] = 0;

			# expand all rendered vertices into crosses shown with the very same color,
			# and check that none vertex was detected twice -- since each is induced from two different
			# cell (at least) trios, existence of two overlapping is possible to exist only by mistake
			detectedVertices = []
			for offset in range(len(vPixels)):
				if vPixels[offset] > 0:
					detectedVertices.append(offset)

					if vPixels[offset] > 1:
						y = int(offset/w)
						x = offset - y*w
						print("  WARNING: Duplicate vertex at ["+str(x)+","+str(y)+"], and that should not be like that.")

			for offset in detectedVertices:
				y = int(offset/w)
				x = offset - y*w
				if x > 2 and x < w-3 and y > 2 and y < imgHeight-3:
					drawCross([x,y],2,vPixels[offset], vPixels,w)

			if len(detectedVertices) != (len(vertices)-len(verticesIgnoredIdxs)):
				print("  WARNING: Control check failed: detectedVertices="+str(len(detectedVertices))+" is not discoveredVerticesCnt - duplicateVerticesCnt")

			print("  Generating triangles and calculating their cell alignment indices...")

			# DEBUG
			# render all triangles
			tPixels = [0 for o in range(w * imgHeight)]

			# for the average cell alignment index
			Q = 0
			aSum = 0
			# list of individual values of q (one per triangle)
			qs = []
			negativeAreaCnt = 0

			# create triangles around the vertices:
			triangles = []
			for i in range(len(vertices)):
				if i not in verticesIgnoredIdxs:
					v = vertices[i]
					if len(v) == 3:
						# triangle
						nuclA = v.pop()
						A = [ nucleiMap[nuclA].CentreX, nucleiMap[nuclA].CentreY ]
						nuclB = v.pop()
						B = [ nucleiMap[nuclB].CentreX, nucleiMap[nuclB].CentreY ]
						nuclC = v.pop()
						C = [ nucleiMap[nuclC].CentreX, nucleiMap[nuclC].CentreY ]
						A,B,C = makeCCWorder(A,B,C)

						drawLine(A,B, 10, vPixels,w)
						drawLine(B,C, 10, vPixels,w)
						drawLine(C,A, 10, vPixels,w)

						# correct the triangle after the distortion from the 3D->2D projection
						AA,BB,CC = createProper2dTriangle(A,B,C, realCoordinates)

						if doTriangleMethodParanoid:
							# the triangle in (the original) 3D
							aa = getPixelAtRealPos(realCoordinates, A[0],A[1])
							bb = getPixelAtRealPos(realCoordinates, B[0],B[1])
							cc = getPixelAtRealPos(realCoordinates, C[0],C[1])

							l1,a1,l2,a2,l3 = getAnglesAndLengthsOfTriangle(bb,aa,cc)
							L1,A1,L2,A2,L3 = getAnglesAndLengthsOfTriangle(BB,AA,CC)
							if math.fabs(l1-L1) > 0.0001 or math.fabs(l2-L2) > 0.0001 or math.fabs(l3-L3) > 0.0001 or math.fabs(a1-A1) > 0.0001 or math.fabs(a2-A2) > 0.0001:
								print("WARNING: proper 2D triangle is not corresponding to 3D original triangle.")

						area,q = computeAreaAndElongationNematic_nonNumpy(BB,AA,CC)
						if area < 0:
							negativeAreaCnt = negativeAreaCnt+1

						Q = Q + area*q
						aSum = aSum + area
						qs.append(q)

						nucleiMap[nuclA].Qsum += area*q
						nucleiMap[nuclA].Qcnt += area
						nucleiMap[nuclB].Qsum += area*q
						nucleiMap[nuclB].Qcnt += area
						nucleiMap[nuclC].Qsum += area*q
						nucleiMap[nuclC].Qcnt += area

						draw2DCCWTriangle(A,B,C, q, tPixels,w)

						# DEBUG REMOVE ME
						#drawCross( [(A[0]+B[0]+C[0])/3.0, (A[1]+B[1]+C[1])/3.0], 5, 80, vPixels,w)
					else:
						# moreAngle ;)
						# determine the centre point first
						C = [ 0.0,0.0 ]
						for nucl in v:
							C[0] = C[0] + nucleiMap[nucl].CentreX
							C[1] = C[1] + nucleiMap[nucl].CentreY

						C[0] = C[0] / float(len(v))
						C[1] = C[1] / float(len(v))

						# now sort the triangles' centres according to azimuth angles
						angSortedM = {} # M = map
						for nucl in v:
							ang = math.atan2( nucleiMap[nucl].CentreY - C[1], nucleiMap[nucl].CentreX - C[0] )

							# make sure we are not loosing this nucl because of the same azimuth
							while ang in angSortedM:
								print("WARNING: this is very unexpected! 3 mutualy neighboring cells in a line!?")
								ang = ang+0.001

							angSortedM[ang] = nucl

						# get array of the angles, sort it, sweep it
						angSortedL = sorted(angSortedM.keys()) # L = List

						for i in range(1,len(angSortedL)):
							nuclA = angSortedM[angSortedL[ i-1 ]]
							A = [ nucleiMap[nuclA].CentreX, nucleiMap[nuclA].CentreY ]
							nuclB = angSortedM[angSortedL[ i ]]
							B = [ nucleiMap[nuclB].CentreX, nucleiMap[nuclB].CentreY ]
							A,B,C = makeCCWorder(A,B,C)

							drawLine(A,B, 15, vPixels,w)
							drawLine(B,C, 15, vPixels,w)
							drawLine(C,A, 15, vPixels,w)

							# correct the triangle after the distortion from the 3D->2D projection
							AA,BB,CC = createProper2dTriangle(A,B,C, realCoordinates)

							area,q = computeAreaAndElongationNematic_nonNumpy(BB,AA,CC)
							if area < 0:
								negativeAreaCnt = negativeAreaCnt+1

							Q = Q + area*q
							aSum = aSum + area
							qs.append(q)

							nucleiMap[nuclA].Qsum += area*q
							nucleiMap[nuclA].Qcnt += area
							nucleiMap[nuclB].Qsum += area*q
							nucleiMap[nuclB].Qcnt += area

							draw2DCCWTriangle(A,B,C, q, tPixels,w)

							# DEBUG REMOVE ME
							#drawCross( [(A[0]+B[0]+C[0])/3.0, (A[1]+B[1]+C[1])/3.0], 5, 80, vPixels,w)

						# add the last triangle
						nuclA = angSortedM[angSortedL[ 0 ]]
						A = [ nucleiMap[nuclA].CentreX, nucleiMap[nuclA].CentreY ]
						nuclB = angSortedM[angSortedL[ len(angSortedL)-1 ]]
						B = [ nucleiMap[nuclB].CentreX, nucleiMap[nuclB].CentreY ]
						A,B,C = makeCCWorder(A,B,C)

						drawLine(A,B, 15, vPixels,w)
						drawLine(B,C, 15, vPixels,w)
						drawLine(C,A, 15, vPixels,w)

						# correct the triangle after the distortion from the 3D->2D projection
						AA,BB,CC = createProper2dTriangle(A,B,C, realCoordinates)

						area,q = computeAreaAndElongationNematic_nonNumpy(BB,AA,CC)
						if area < 0:
							negativeAreaCnt = negativeAreaCnt+1

						Q = Q + area*q
						aSum = aSum + area
						qs.append(q)

						nucleiMap[nuclA].Qsum += area*q
						nucleiMap[nuclA].Qcnt += area
						nucleiMap[nuclB].Qsum += area*q
						nucleiMap[nuclB].Qcnt += area

						draw2DCCWTriangle(A,B,C, q, tPixels,w)

						# DEBUG REMOVE ME
						#drawCross( [(A[0]+B[0]+C[0])/3.0, (A[1]+B[1]+C[1])/3.0], 5, 80, vPixels,w)

			ImagePlus( "junctionPointsAsCrosses_withInducedTriangles", FloatProcessor(w,imgHeight, vPixels) ).show()
			ImagePlus( "cell_alignment_index_per_triangle",            FloatProcessor(w,imgHeight, tPixels) ).show()

			scatterData.append("# Q\tp\tdist from ["+str(tCentreX)+","+str(tCentreY)+"] where p is ShapeFactor\n")

			# finish Q, and obtain value of the pCurve at Q
			# global Q
			Q = Q / aSum
			#
			# local Qs
			for nucl in nuclei:
				if nucl.Qcnt > 0:
					nucl.Qsum /= nucl.Qcnt

					# also report data for the scatter plot
					coords = []
					reportInterpolatedPoints(coords, nucl.CentreX,nucl.CentreY, tCentreX,tCentreY)
					scatterData.append(str(nucl.Qsum)+"\t"+str(nucl.ShapeFactor)+"\t"+str(properLength(coords,realCoordinates))+"\n")
				else:
					print("  Cell ID "+nucl.Color+" was really not part of any triangle!?")

			print("Q= "+str(Q)+"   pCurve(Q)= "+str(pCurveOfQ(Q)))
			print("negativeAreaCnt="+str(negativeAreaCnt)+"  ...must be 0!")

			qsHistImg = ImagePlus( "local_cell_alignment_indices", FloatProcessor(1,len(qs), qs) )
			IJ.run(qsHistImg,  "Histogram", "20")

			if showShapeFactorImage:
				# render the nuclei again with shapeFactors - pCurveAtQ
				SAthres = [0 for o in range(w * imgHeight)]

				for nucl in nuclei:
					pCurveAtQ = pCurveOfQ(nucl.Qsum)
					for pix in nucl.Pixels:
						SAthres[pix[1]*w + pix[0]] = nucl.ShapeFactor - pCurveAtQ

					nucl.DrawValue = nucl.Qsum

				ImagePlus( "realShapeFactors_minus_predictedTransitionShapeFactor", FloatProcessor(w,imgHeight, SAthres) ).show()
				drawChosenNucleiValue(originalImageName+": Alignment index per cell", imp.getWidth(),imp.getHeight(), nuclei)

		else:
			print("Skipped the requested Triangle method because it currently works "
			     +"only together with \"Polygon boundary straightening\" enabled")


	if (showRawData):
		print("Populating table...")

		# create an output table with three columns: label, circularity, area, size, positionX, positionY
		rt = ResultsTable()

		# also create two hidden 1D images (arrays essentially) and ask to display their histograms later
		imgArea = []
		imgCirc = []
		imgNeig = []

		for nucl in nuclei:
			rt.incrementCounter()
			rt.addValue("label"                            ,nucl.Color)
			rt.addValue("circularity (higher more roundish)",nucl.Circularity)
			rt.addValue("circularity (pixel-based)"        ,nucl.DrawValue) # VLADO PIXEL CIRC DEBUG
			rt.addValue("shape factor"                     ,nucl.ShapeFactor)
			rt.addValue("area (um^2)"                      ,nucl.Area)
			rt.addValue("area (px)"                        ,nucl.Size)
			rt.addValue("perimeter (px)"                   ,nucl.EdgeSize)
			rt.addValue("perimeter (um)"                   ,nucl.EdgeLength)
			rt.addValue("neigbor count"                    ,len(nucl.NeighIDs))
			rt.addValue("centreX (px)"                     ,nucl.CentreX)
			rt.addValue("centreY (px)"                     ,nucl.CentreY)

			imgArea.append(nucl.Area)
			imgCirc.append(nucl.Circularity)
			imgNeig.append(len(nucl.NeighIDs))

		# show the image
		rt.showRowNumbers(False)
		rt.show("Nuclei properties")

		# show the histograms
		#imgArea = ImagePlus("areas of nuclei",FloatProcessor(len(nuclei),1,imgArea))
		imgArea = ImagePlus("nuclei_areas",FloatProcessor(len(nuclei),1,imgArea))
		IJ.run(imgArea, "Histogram", str( (imgArea.getDisplayRangeMax() - imgArea.getDisplayRangeMin()) / 10 ))

		#imgCirc = ImagePlus("circularities of nuclei",FloatProcessor(len(nuclei),1,imgCirc))
		imgCirc = ImagePlus("nuclei_circularities",FloatProcessor(len(nuclei),1,imgCirc))
		IJ.run(imgCirc, "Histogram", "20")

		imgNeig = ImagePlus("nuclei_neigborCount",FloatProcessor(len(nuclei),1,imgNeig))
		IJ.run(imgNeig, "Histogram", "10")

		# debug: what perimeter points are considered
		# writeCoordsToFile(nuclei[0].EdgePixels,"/Users/ulman/DATA/fp_coords_0.txt")
		# writeCoordsToFile(nuclei[1].EdgePixels,"/Users/ulman/DATA/fp_coords_1.txt")

	removeMeImg.changes = False
	removeMeImg.close()


def startSession(folder,tpFile):
	IJ.open(folder+"/"+tpFile)
	IJ.selectWindow(tpFile);

def closeSession(folder,tpFile):
	if doTriangleMethod:
		closeSession_TriangleMethod(folder,tpFile)

	IJ.selectWindow(tpFile+": NEW SHAPES");
	IJ.getImage().close();

	IJ.selectWindow("1_labelled_image");
	IJ.getImage().changes = False
	IJ.getImage().close();

	IJ.selectWindow("upScaledOrigImg.tif");
	IJ.getImage().changes = False
	IJ.getImage().close();

	IJ.selectWindow(tpFile);
	IJ.getImage().close();


def closeSession_TriangleMethod(folder,tpFile):
	if showShapeFactorImage:
		IJ.save(IJ.getImage(),folder+"/"+tpFile+"__cellAlignmentIndices_perCell.tif")
		IJ.getImage().close();

		IJ.save(IJ.getImage(),folder+"/"+tpFile+"__cellShapeIndices_minusPredictedThreshold.tif")
		IJ.getImage().close();

	IJ.save(IJ.getImage(),folder+"/"+tpFile+"__histogramOfqs.tif")
	IJ.getImage().close();

	IJ.selectWindow("cell_alignment_index_per_triangle")
	IJ.save(IJ.getImage(),folder+"/"+tpFile+"__cellAlignmentIndices_perTriangle.tif")
	IJ.getImage().close();

	IJ.selectWindow("junctionPointsAsCrosses_withInducedTriangles")
	IJ.save(IJ.getImage(),folder+"/"+tpFile+"__verticesAndTriangles.tif")
	IJ.getImage().close();

	if showShapeFactorImage:
		IJ.save(IJ.getImage(),folder+"/"+tpFile+"__cellShapeIndices_akaShapeFactor.tif")
		IJ.getImage().close();


def doOneTP(tpFile, tCntrX,tCntrY):
	global tCentreX
	global tCentreY
	global scatterData

	print(tpFile+" Starting.............")
	inFolder  = "/home/ulman/data/AJ__ZenKD/curated/"
	outFolder = "/home/ulman/data/AJ__ZenKD/curated/"

	startSession(inFolder,tpFile)
	tCentreX = tCntrX
	tCentreY = tCntrY
	scatterData = []
	main()
	saveScatterPlot(outFolder+"/"+tpFile+"__scatterData.txt")
	print(tpFile+" Done.")
	closeSession(outFolder,tpFile)


def saveScatterPlot(filename):
	print("Saving scatter data: "+filename)
	ff = open(filename,"w")
	for scLine in scatterData:
		ff.write(scLine)
	ff.close()


# HAVE UNCOMMENTED EITHER THESE TWO/THREE LINES, OR ALL THE LINES UNDERNEATH THESE TWO
# single, currently opened image mode
#main()
#saveScatterPlot("/tmp/scatterData.txt")
#print("Done.")


# batch processing mode
#doOneTP("10.tif", 760,1285)
#doOneTP("310.tif",760,1285)
#doOneTP("340.tif",630,1290)
#doOneTP("425.tif",438,1310)
#doOneTP("555.tif",452,1330)

# ZenKD
areaMin = 20
prepareMapFilePaths(mapFolder.getAbsolutePath()+"/0")
doOneTP("0.tif", 851,1130)

areaMin = 100
prepareMapFilePaths(mapFolder.getAbsolutePath()+"/90")
doOneTP("90.tif", 940,1344)

prepareMapFilePaths(mapFolder.getAbsolutePath()+"/114")
doOneTP("114.tif", 930,1298)

prepareMapFilePaths(mapFolder.getAbsolutePath()+"/137")
doOneTP("137.tif", 998,1864)
