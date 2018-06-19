#@String (label="Output files prefix") outPrefix
#@File (style="directory", label="Output directory") outDir
outDir = outDir.getAbsolutePath()

from ij import IJ
imp = IJ.getImage()

def writeFile_constant(fileName):
	f = open(fileName,"w")

	# write all lines (that end with '\n') except the last one
	for y in range(1,imp.height):
		for x in range(1,imp.width):
			f.write("1 ")
		f.write("1\n")

	# the last one
	for x in range(1,imp.width):
		f.write("1 ")
	f.write("1")

	f.close()


def writeFile_column(fileName):
	f = open(fileName,"w")

	# write all lines (that end with '\n') except the last one
	for y in range(1,imp.height):
		for x in range(1,imp.width):
			f.write(str(x-1)+" ")
		f.write(str(imp.width-1)+"\n")

	# the last one
	for x in range(1,imp.width):
		f.write(str(x-1)+" ")
	f.write(str(imp.width-1))

	f.close()


def writeFile_row(fileName):
	f = open(fileName,"w")

	# write all lines (that end with '\n') except the last one
	for y in range(1,imp.height):
		for x in range(1,imp.width):
			f.write(str(y-1)+" ")
		f.write(str(y-1)+"\n")

	# the last one
	for x in range(1,imp.width):
		f.write(str(imp.height-1)+" ")
	f.write(str(imp.height-1))

	f.close()


def main():
	writeFile_constant(outDir+"/"+outPrefix+"_areas.txt")
	writeFile_constant(outDir+"/"+outPrefix+"_coords_Z.txt")

	writeFile_column(outDir+"/"+outPrefix+"_coords_X.txt")
	writeFile_row(outDir+"/"+outPrefix+"_coords_Y.txt")


main()
