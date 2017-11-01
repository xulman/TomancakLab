from ij import IJ
from ij import ImagePlus
import sys

def readRealSizesUI():
	# ask for input file
	AreaFile = IJ.getFilePath("Choose your pixel areas, Matlab exported file:")
	if (AreaFile is None):
			sys.exit('User canceled Dialog!')

	# and the call the main worker
	return readRealSizes(AreaFile)


def readRealSizes(aFile):
	if (aFile is None):
			sys.exit('Missing input file!')

	# open the selected file
	IJ.run("Text Image... ", "open="+aFile);

	# get pixel 1D array, and image sizes
	imp = IJ.getImage();
	rawPixels = imp.getProcessor().getPixels();
	hh = imp.height;
	ww = imp.width;

	# convert the data array to "2D image", and close it
	realSizes = [[rawPixels[y*ww +x] for y in range(hh)] for x in range(ww)]
	imp.close();

	# and return the "2D pixel areas"
	return realSizes;


def checkSize2DarrayVsImgPlus(array, imp):
	if (len(array) != imp.width):
		sys.exit('x dimension mismatch!')

	if (len(array[0]) != imp.height):
		sys.exit('y dimension mismatch!')

