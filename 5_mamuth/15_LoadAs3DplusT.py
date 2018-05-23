#@int (label="Starting timepoint:") fromT
#@int (label="Ending timepoint:") tillT
#@File (style="directory", label="Image folder:") path
#@String (label="Input file suffix (e.g. _C0.tif):") inFileSuffix
path = path.getAbsolutePath()

from ij import IJ
from ij import ImagePlus

# the amount of time points that shall be processed
spanT = tillT-fromT+1

# open the first image to have "seed of the bigBoy"
IJ.open(path+"/T"+str(fromT)+inFileSuffix);
img = IJ.getImage()
img.setTitle("bigBoy.tif")

zSlicesCnt = img.getNSlices()

for t in range(fromT+1,tillT+1):
	IJ.open(path+"/T"+str(t)+inFileSuffix);
	IJ.run("Concatenate...", "image1=bigBoy.tif image2=T"+str(t)+inFileSuffix+" image3=[-- None --]");
	img = IJ.getImage()
	img.setTitle("bigBoy.tif")

IJ.run("Stack to Hyperstack...", "order=xyztc channels=1 slices="+str(zSlicesCnt)+" frames="+str(spanT)+" display=Grayscale");
