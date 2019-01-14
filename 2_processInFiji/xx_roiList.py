from ij import IJ
from ij.gui import PolygonRoi, Roi

def reportPointsOnALine(coords, x1,y1, x2,y2):
	stepsNo = max( abs(x2-x1),abs(y2-y1) )

	dx = float(x2-x1) / float(stepsNo)
	dy = float(y2-y1) / float(stepsNo)

	for s in range(stepsNo):
		coords.append( [int(x1 + s*dx),int(y1 + s*dy)] )

	return coords


def collectAndReportROIPoints():
	# Get current ROI, i.e. from the current slice
	# Get current ImagePlus
	image = IJ.getImage();
	roi = image.getRoi()

	if roi is not None:
		print "Coordinates processed for frame "+str(image.getSlice())

		polygon = roi.getPolygon()
		x = polygon.xpoints
		y = polygon.ypoints

		coords = []
		for i in range(1,polygon.npoints):
			reportPointsOnALine(coords, x[i-1],y[i-1], x[i],y[i])

		for c in coords:
			print("x="+str(c[0])+", y="+str(c[1]))
		return coords
	else:
		print "No ROI is available for frame "+str(image.getSlice())
		return []

# collectAndReportROIPoints()


def collectAndReportROIInnerPoints():
	# Get current ROI, i.e. from the current slice
	# Get current ImagePlus
	image = IJ.getImage();
	roi = image.getRoi()

	if roi is not None:
		print "Coordinates processed for frame "+str(image.getSlice())

		coords = []
		for p in roi.getContainedPoints():
			coords.append( [p.x,p.y] )

		for c in coords:
			print("x="+str(c[0])+", y="+str(c[1]))
		return coords
	else:
		print "No ROI is available for frame "+str(image.getSlice())
		return []

collectAndReportROIInnerPoints()
