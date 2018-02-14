import math


class Nucleus:

	def __init__(self,Color,Pixels,ip,realSizes):
		# label of the nuclei
		self.Color = Color

		# list of pixels that make up this nuclei (nuclei mask)
		self.Pixels = Pixels

		# object area in squared microns
		self.Area = 0.0
		# object area in pixel number
		self.Size = len(Pixels)

		# geometric centre in pixel coordinates
		self.CentreX = 0.0
		self.CentreY = 0.0

		# calculate real size and geometrical centre
		for pix in Pixels:
			self.Area += realSizes[pix[0]][pix[1]]
			self.CentreX += pix[0]
			self.CentreY += pix[1]

		# finish calculation of the geometrical centre
		self.CentreX /= len(Pixels)
		self.CentreY /= len(Pixels)

		# list of pixels that make up boundary of this nuclei (nuclei mask)
		self.EdgePixels = []

		# (approximate) length of the boundary in microns
		self.EdgeLength = 0

		# determine boundary pixels
		for pix in Pixels:
			try:
				ColorLeft = ip.getPixel(pix[0]-1,pix[1])
			except:
				ColorLeft = - 1

			try:
				ColorAbove = ip.getPixel(pix[0],pix[1]-1)
			except:
				ColorAbove = -1

			thisColor = ip.getPixel(pix[0],pix[1])

			try:
				ColorBelow = ip.getPixel(pix[0],pix[1]+1)
			except:
				ColorBelow = -1

			try:
				ColorRight = ip.getPixel(pix[0]+1,pix[1])
			except:
				ColorRight = -1

			# mimics 2D 4-neighbor erosion
			if thisColor != ColorLeft or thisColor != ColorAbove or thisColor != ColorBelow or thisColor != ColorRight:
				self.edgePixels.append([pix[0],pix[1]])

		# TODO: edgeSize has to be edgeLength !!! involve proper length measurement, see issue #1
		self.edgeSize = 0
		for pix in self.edgePixels:
			self.edgeSize += realSizes[pix[0]][pix[1]]

		# TODO: edgeSize has to be edgeLength !!! involve proper length measurement, see issue #1
		# lower value means higher circularity
		self.circularity = abs(self.area - ((self.edgeSize**2)/(4*math.pi)))/self.area

	# the same condition that every one should use to filter out nuclei that

	# the same condition that everyone should use to filter out nuclei that
	# do not qualify for this study
	def doesQualify(self, areaConsidered,areaMin,areaMax, circConsidered,circMin,circMax):
		if (circConsidered == True and (self.Circularity < circMin or self.Circularity > circMax)):
			return False;
		if (areaConsidered == True and (self.Area < areaMin or self.Area > areaMax)):
			return False;
		return True;
