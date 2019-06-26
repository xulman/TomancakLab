from __future__ import print_function
from ij import IJ

#@boolean (label="Report also individual values") showRawValues


def thresholdStack(img):
	for z in range(1,img.getNSlices()+1):
		img.setZ(z)
		pxs = img.getProcessor().getPixels()
		for o in range(len(pxs)):
			if pxs[o] > 0.001:
				pxs[o] = 0
			else:
				pxs[o] = 255


# extract the ROI-only area from the image
imgMask = IJ.getImage().duplicate()
imgMask.show()

# again, extract the ROI-only area from the image...
imgRaw = IJ.getImage().duplicate()
imgRaw.show()

# ...and determine nuclei boundaries and CCA based on them...
IJ.selectWindow(imgMask.getTitle())
IJ.run("Find Edges")
thresholdStack(imgMask)
imgMask.updateAndRepaintWindow()

IJ.selectWindow(imgMask.getTitle())
IJ.run("Grays")
IJ.run("Enhance Contrast", "saturated=0.35");
IJ.run("8-bit")
IJ.run("Enhance Contrast", "saturated=0.35");
IJ.run("Dilate","stack")

# ...into another image showing now the instance segmentation,
IJ.run(imgMask,"Threshold to label map (2D, 3D)", "threshold=20")
imgLabel = IJ.getImage()

# close the "boundary" image
imgMask.changes = False
imgMask.close()

# find previously unseen labels and check original (raw) values
# from the corresponding original (raw) image
for z in range(1,imgRaw.getNSlices()+1):
	imgRaw.setZ(z)
	imgLabel.setZ(z)

	rp = imgRaw.getProcessor().getPixels()
	lp = imgLabel.getProcessor().getPixels()

	seenRawValues = []
	rawValSum = 0

	seenLabels = []

	for offset in range(len(lp)):
		label = lp[offset]
		if label > 0 and not label in seenLabels:
			seenLabels.append(label)
			seenRawValues.append(rp[offset])
			rawValSum += rp[offset]

	print("z="+str(z)+" avg="+str(float(rawValSum)/float(len(seenRawValues)))
		+" cnt="+str(len(seenRawValues)),end='')
	if showRawValues:
		print(" values: ",end='')
		for r in sorted(seenRawValues):
			print(r,end=' ')
	print()
