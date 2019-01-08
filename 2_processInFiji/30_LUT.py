#@String  (label="Define bins, e.g. -10-20-30-") binInString
#@String  (label="Define output values per bin, e.g. 0,2,3,5") binOutString
#@boolean (label="Create output demo image instead?") createDemo

from ij import IJ
from ij import ImagePlus
from ij.process import FloatProcessor

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


def parseBinBoundaries(valString):
	outVals = []

	a = 1
	b = valString.find('-',a)
	if b == -1:
		print("bin string should always end with '-'")
		return outVals

	while a < b:
		v = float(valString[a:b])
		outVals.append(v)

		a = b+1
		b = valString.find('-',a)

	return outVals


def parseBinValues(valString):
	outVals = []

	a = 0
	b = valString.find(',')
	if b == -1:
		b = len(valString)

	while a < b:
		v = float(valString[a:b])
		outVals.append(v)

		a = b+1
		b = valString.find(',',a)
		if b == -1:
			b = len(valString)

	return outVals


def main():
	binOutValues = parseBinValues(binOutString)
	binNo = len(binOutValues)

	if createDemo:
		print("Creating demo for these values:")
		print(binOutValues)

		sqW = 20
		sqH = 20

		sqArea = sqW * sqH
		demoPixels = [ binOutValues[int(offset/sqArea)] for offset in range(sqArea*binNo) ]
		ImagePlus("demo LUT", FloatProcessor(sqW,sqH*binNo,demoPixels)).show()
	else:
		binInBoundaries = parseBinBoundaries(binInString)

		if len(binInBoundaries)+1 != binNo:
			print("Number of defined bins ("+str(len(binInBoundaries)+1)+") does not match number of output values ("+str(binNo)+")")
			return

		# report LUT
		print("[min - "+str(binInBoundaries[0])+"] -> "+str(binOutValues[0]))
		for i in range(binNo-2):
			print("("+str(binInBoundaries[i])+" - "+str(binInBoundaries[i+1])+"] -> "+str(binOutValues[i+1]))
		print("("+str(binInBoundaries[binNo-2])+" - max] -> "+str(binOutValues[binNo-1]))

		# apply on the currently selected image
		imp = IJ.getImage()
		oldZ = imp.getZ()

		for z in range(1,imp.getNSlices()+1):
			imp.setZ(z)
			pixels = imp.getProcessor().getPixels()

			for p in range(len(pixels)):
				if pixels[p] <= binInBoundaries[0]:
					pixels[p] = binOutValues[0]
				elif pixels[p] > binInBoundaries[binNo-2]:
					pixels[p] = binOutValues[binNo-1]
				else:
					# keep moving through "inside" intervals and keep testing
					# don't assume they are sorted...

					for i in range(binNo-2):
						if binInBoundaries[i] < pixels[p] and pixels[p] <= binInBoundaries[i+1]:
							pixels[p] = binOutValues[i+1]
							break

		imp.setZ(oldZ)


main()
