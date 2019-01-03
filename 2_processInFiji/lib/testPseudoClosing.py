#@int(label="stop latest after this no. of rounds") maxRounds
#@int(label="stop if there was less than this no. of pixel changes") minPixelChanges
from ij import IJ


# returns a map of pixel values around this pixel,
# the pixel values are stored as keys in this map (and are hence unique),
# the pixel is given with its offset 'o' in the 2D image (array) 'i'
# whose width is 'w' and height is 'h'; the output map is actually
# a histogram of pixels in 8-neighborhood around the input pixel
def findUniqueNeighbors(i,o,w,h):
	h = {}
	for x in [-w-1,-w,-w+1, -1,1, +w-1,+w,+w+1]:
		v = i[o+x]
		if v in h:
			h[v] = h[v]+1
		else:
			h[v] = 1

	return h


def pseudoClosing(imp):
	i = imp.getProcessor().getPixels()
	w = imp.getWidth()
	h = imp.getHeight()

	# have a copy of the original so that "neighborhood computations"
	# are not affected by the on-going processing
	I = [ i[o] for o in range(len(i)) ]

	countChanges = 0

	for y in range(1,h-1):
		for x in range(1,w-1):
			# offset
			o = y*w + x

			if I[o] == 0:
				# found empty/black pixel,
				# is it surrounded only by the same non-zero colour?
				h = findUniqueNeighbors(I,o,w,h)

				v = h.keys()
				# one-bin histogram: surrounded by fg voxels?
				if len(v) == 1 and v[0] > 0:
					i[o] = v[0]
					countChanges = countChanges+1

				# two-bins histogram: surrounded by bg and in majority by single-fg voxels?
				if len(v) == 2 and v[0] == 0 and h[v[1]] > 4:
					i[o] = v[1]
					countChanges = countChanges+1
				if len(v) == 2 and v[1] == 0 and h[v[0]] > 4:
					i[o] = v[0]
					countChanges = countChanges+1

	return countChanges


def pseudoDilation(imp):
	i = imp.getProcessor().getPixels()
	w = imp.getWidth()
	h = imp.getHeight()

	# have a copy of the original so that "neighborhood computations"
	# are not affected by the on-going processing
	I = [ i[o] for o in range(len(i)) ]

	countChanges = 0

	for y in range(1,h-1):
		for x in range(1,w-1):
			# offset
			o = y*w + x

			if I[o] == 0:
				# found empty/black pixel,
				# is it surrounded only by the same non-zero colour?
				h = findUniqueNeighbors(I,o,w,h)

				v = h.keys()
				# one-bin histogram: surrounded by fg voxels?
				if len(v) == 1 and v[0] > 0:
					i[o] = v[0]
					countChanges = countChanges+1

				# two-bins histogram: surrounded by bg and by single-fg voxels?
				if len(v) == 2 and v[0] == 0:
					i[o] = v[1]
					countChanges = countChanges+1
				if len(v) == 2 and v[1] == 0:
					i[o] = v[0]
					countChanges = countChanges+1

	return countChanges


def testing():
	imp = IJ.getImage()
	i = imp.getProcessor().getPixels()
	w = imp.getWidth()
	h = imp.getHeight()
	o = 69012
	print findUniqueNeighbors(i,o,w,h)

	o = 69011
	print findUniqueNeighbors(i,o,w,h)

	o = 69010
	print findUniqueNeighbors(i,o,w,h)


def pluginCode():
	imp = IJ.getImage()

	for i in range(maxRounds):
		cnt = pseudoClosing(imp)
		imp.updateAndRepaintWindow()

		print "done iteration #"+str(i+1)+", and saw "+str(cnt)+" changes"

		if cnt <= minPixelChanges:
			break;

	cnt = pseudoDilation(imp)
	imp.updateAndRepaintWindow()
	print "finito with final dilation, saw "+str(cnt)+" changes"


def experimenting():
	IJ.run("32-bit");
	IJ.run("8-bit");
	IJ.run("Invert");
	IJ.run("Skeletonize","BlackBackground=false");

	#here CCA!

	imp = IJ.getImage()
	pseudoClosing(imp)
	imp.updateAndRepaintWindow()


# if running the function fails, it's likely because maxRounds and minPixelChanges
# are not defined, which happens when this script is not called as a Fiji plugin --
# in which case we don't want this function to be executed...
try:
	pluginCode()
except NameError:
	useLess = True
