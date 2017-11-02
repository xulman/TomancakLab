from ij import IJ
from ij import ImagePlus
import sys

# ---------- real areas ----------
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


# ---------- real 3D coordinates ----------
def readRealCoordsUI():
	# ask for input files
	XcoordFile = IJ.getFilePath("Choose your X pixel coordinates, Matlab exported file:")
	YcoordFile = IJ.getFilePath("Choose your Y pixel coordinates, Matlab exported file:")
	ZcoordFile = IJ.getFilePath("Choose your Z pixel coordinates, Matlab exported file:")
	if (XcoordFile is None) or (YcoordFile is None) or (ZcoordFile is None):
			sys.exit('User canceled Dialog!')

	# and the call the main worker
	return readRealCoords(XcoordFile,YcoordFile,ZcoordFile)


def readRealCoords(xFile, yFile, zFile):
	if (xFile is None) or (yFile is None) or (zFile is None):
			sys.exit('Missing input file(s)!')

	# open the selected files
	IJ.run("Text Image... ", "open="+xFile);

	# get pixel 1D array, and image sizes
	imp = IJ.getImage();
	rawPixelsX = imp.getProcessor().getPixels();
	hh = imp.height;
	ww = imp.width;
	imp.close();

	#y:
	IJ.run("Text Image... ", "open="+yFile);
	imp = IJ.getImage();
	checkSizeExplicitVsImgPlus(ww,hh, imp);
	rawPixelsY = imp.getProcessor().getPixels();
	imp.close();

	#z:
	IJ.run("Text Image... ", "open="+zFile);
	imp = IJ.getImage();
	checkSizeExplicitVsImgPlus(ww,hh, imp);
	rawPixelsZ = imp.getProcessor().getPixels();
	imp.close();

	# convert the data array to "3D image"
	real3DCoords = [[ [rawPixelsX[y*ww +x],rawPixelsY[y*ww +x],rawPixelsZ[y*ww +x]] for y in range(hh)] for x in range(ww)]

	# and return it
	return real3DCoords;


# ---------- helper functions ----------
def checkSize2DarrayVsImgPlus(array, imp):
	if (len(array) != imp.width):
		sys.exit('x dimension mismatch!')

	if (len(array[0]) != imp.height):
		sys.exit('y dimension mismatch!')


def checkSizeExplicitVsImgPlus(ww,hh, imp):
	if (ww != imp.width):
		sys.exit('x dimension mismatch!')

	if (hh != imp.height):
		sys.exit('y dimension mismatch!')

