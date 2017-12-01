import math


class Nucleus:

	def __init__(self,Pixels,Color):
		# list of pixels that make up this nuclei (nuclei mask)
		self.Pixels = Pixels

		# label of the nuclei
		self.Color = Color

		# in squared microns
		self.area = 0.0
		# in pixel count
		self.size = len(Pixels)

		# geometric centre in pixel coordinates
		self.centreX = 0.0
		self.centreY = 0.0

		for pix in Pixels:
			self.area += realSizes[pix[0]][pix[1]]
			self.centreX += pix[0]
			self.centreY += pix[1]

		# finish calculation of the geometrical centre
		self.centreX /= len(Pixels)
		self.centreY /= len(Pixels)

		self.edgePixels = []
		for pix in Pixels:
			thisColor = ip.getPixel(pix[0],pix[1])
			try:
				ColorLeft = ip.getPixel(pix[0]-1,pix[1])
			except:
				ColorLeft = - 1

			try:
				ColorAbove = ip.getPixel(pix[0],pix[1]-1)
			except:
				ColorAbove = -1

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
