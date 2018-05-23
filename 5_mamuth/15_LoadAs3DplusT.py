#@int (label="Starting timepoint:") fromT
#@int (label="Ending timepoint:") tillT
#@int (label="Chunk size of timepoints:") chunkT
#@File (style="directory", label="Image folder:") path
#@String (label="Input file suffix (e.g. _C0.tif):") inFileSuffix
#@String (label="Output file prefix (e.g. membraneSegmentation_):") outFilePrefix
path = path.getAbsolutePath()

from ij import IJ
from ij import ImagePlus

for fT in range(fromT,tillT+1,chunkT):
	tT = min(fT+chunkT-1,tillT)
	spanT = tT-fT+1

	print "doing range: "+str(fT)+" - "+str(tT)

	# open the first image to have "seed of the bigBoy"
	IJ.open(path+"/T"+str(fT)+inFileSuffix);
	img = IJ.getImage()
	img.setTitle("bigBoy.tif")

	zSlicesCnt = img.getNSlices()

	for t in range(fT+1,tT+1):
		IJ.open(path+"/T"+str(t)+inFileSuffix);
		IJ.run("Concatenate...", "image1=bigBoy.tif image2=T"+str(t)+inFileSuffix+" image3=[-- None --]");
		img = IJ.getImage()
		img.setTitle("bigBoy.tif")

	IJ.run("Stack to Hyperstack...", "order=xyztc channels=1 slices="+str(zSlicesCnt)+" frames="+str(spanT)+" display=Grayscale");
	IJ.save(path+"/"+outFilePrefix+"batchFrom"+str(fT)+".tif")
	IJ.getImage().close()
