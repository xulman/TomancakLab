#@File (label="Input image file to be split")               inputFile
#@int  (label="First z-slice to start with", value="1")     zSpanFrom
#@int  (label="Last z-slice to end with")                   zSpanTo
#@int  (label="First time-point to start with", value="1")  timeSpanFrom
#@int  (label="Last time-point to end with")                timeSpanTo
#@File (style="directory", label="Output directory with the individual time-points") outputDir

from ij import IJ
import ij.ImagePlus


def main():
	IJ.run("Bio-Formats", "open="+inputFile.getPath()+" color_mode=Default rois_import=[ROI manager] specify_range view=Hyperstack stack_order=XYCZT z_begin="+str(zSpanFrom)+" z_end="+str(zSpanTo)+" z_step=1 t_begin="+str(timeSpanFrom)+" t_end="+str(timeSpanTo)+" t_step=1");
	i = IJ.getImage()

	for T in range(timeSpanFrom, timeSpanTo+1):
		# set the image to the given time point
		i.setT(T -timeSpanFrom+1)

		# initiate a new output image (just with this time point)
		stack = ij.ImageStack(i.getWidth(),i.getHeight())

		# iterate 
		for Z in range(zSpanFrom, zSpanTo+1):
			i.setZ(Z)
			stack.addSlice(i.getProcessor())

		# determine output filename and "report progress bar"
		F = outputDir.getPath() + "/timepoint_" + str(T) + ".tif"
		print "saving: "+F

		# save the created stack image
		IJ.save(ij.ImagePlus(F,stack),F)

	print "done"


main()
