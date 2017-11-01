from ij import IJ
from ij import ImagePlus
import sys

def readRealCoords():
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


def checkSizeExplicitVsImgPlus(ww,hh, imp):
	if (ww != imp.width):
		sys.exit('x dimension mismatch!')

	if (hh != imp.height):
		sys.exit('y dimension mismatch!')

