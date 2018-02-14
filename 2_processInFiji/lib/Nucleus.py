import math

# this section adds a folder, in which this very script is living,
# to the current search paths so that we can import our "library script"
import sys.path
import os.path
import inspect
sys.path.append(os.path.dirname(inspect.getfile(inspect.currentframe())))

# import our "library scripts"
from properMeasurements import *


class Nucleus:

	def __init__(self,Color,Pixels,ip,realSizes,realCoords):
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

			# mimics 2D 4-neighbor erosion:
			# encode which neighbors are missing, and how many of them
			missNeig = 0
			cnt = 0;

			if thisColor != ColorLeft:
				missNeig += 1
				cnt += 1
			if thisColor != ColorAbove:
				missNeig += 2
				cnt += 1
			if thisColor != ColorRight:
				missNeig += 4
				cnt += 1
			if thisColor != ColorBelow:
				missNeig += 8
				cnt += 1

			if missNeig != 0:
				# found border-forming pixel, enlist it
				self.EdgePixels.append([pix[0],pix[1]])

				# Marching-cubes-like determine configuration of the border pixel,
				# and guess an approximate proper length of the boundary this pixels co-establishes
				coords = []

				# legend on bits used to flag directions:
				#
				#           2
				#          (y-)
				#           |
				#           |
				# 1 (x-) <--+--> (x+) 4
				#           |
				#           |
				#          (y+)
				#           8
				#

				if cnt == 1:
					# one neighbor is missing -> boundary is straight here
					if missNeig&1 or missNeig&4:
						# vertical boundary
						coords = [ [pix[0],pix[1]-1] , [pix[0],pix[1]] , [pix[0],pix[1]+1] ]
					else:
						# horizontal boundary
						coords = [ [pix[0]-1,pix[1]] , [pix[0],pix[1]] , [pix[0]+1,pix[1]] ]

				if cnt == 2:
					# two neighbors -> we're either a corner, or boundary is 1px thick
					if missNeig&5 == 5 or missNeig&10 == 10:
						# 1px thick boundary
						if missNeig&5 == 5:
							# 1px thick vertical boundary
							coords = [ [pix[0],pix[1]-1] , [pix[0],pix[1]] , [pix[0],pix[1]+1] , [pix[0],pix[1]] , [pix[0],pix[1]-1] ]
						else:
							# 1px thick horizontal boundary
							coords = [ [pix[0]-1,pix[1]] , [pix[0],pix[1]] , [pix[0]+1,pix[1]] , [pix[0],pix[1]] , [pix[0]-1,pix[1]] ]
					else:
						# missing neighbors are "neighbors" to each other too -> we're a corner
						if missNeig&6 == 6 or missNeig&9 == 9:
							# we're top-right corner, or bottom-left corner
							coords = [ [pix[0]-1,pix[1]-1] , [pix[0],pix[1]] , [pix[0]+1,pix[1]+1] ]

						if missNeig&12 == 12 or missNeig&3 == 3:
							# we're bottom-right corner, or top-left corner
							coords = [ [pix[0]-1,pix[1]+1] , [pix[0],pix[1]] , [pix[0]+1,pix[1]-1] ]

				if cnt == 3:
					# three neighbors -> we're "a blob or a spike" popping out from a straight boundary...
					if missNeig&7 == 7:
						# have only a neighbor below
						coords = [ [pix[0]-1,pix[1]+1] , [pix[0],pix[1]] , [pix[0]+1,pix[1]+1] ]

					if missNeig&11 == 11:
						# have only a neighbor right
						coords = [ [pix[0]+1,pix[1]-1] , [pix[0],pix[1]] , [pix[0]+1,pix[1]+1] ]

					if missNeig&13 == 13:
						# have only a neighbor above
						coords = [ [pix[0]-1,pix[1]-1] , [pix[0],pix[1]] , [pix[0]+1,pix[1]-1] ]

					if missNeig&14 == 14:
						# have only a neighbor left
						coords = [ [pix[0]-1,pix[1]-1] , [pix[0],pix[1]] , [pix[0]-1,pix[1]+1] ]

				# we gracefully ignore when cnt == 4...

				# calculate the proper length of the local boundary by sweeping
				# through a neighbor,myself,neighbor (giving us twice the required length)
				self.EdgeLength += properLength(coords,realCoords) / 2.0

#				#DEBUG VLADO REMOVE
#				a = coords[0]
#				b = coords[1]
#				c = coords[2]
#				for i in [0,1]:
#					a[i] = (float(a[i])+float(b[i]))/2.0
#					c[i] = (float(b[i])+float(c[i]))/2.0
#
#				print str(a[0])+" "+str(a[1])+" 1"
#				print str(b[0])+" "+str(b[1])+" 2"
#				print str(c[0])+" "+str(c[1])+" 1"
#				print ""

		# length of the boundary in pixel
		self.EdgeSize = len(self.EdgePixels)

		# circularity: lower value means higher circularity
		self.Circularity = abs(self.Area - ((self.EdgeLength**2)/(4*math.pi)))/self.Area


	# the same condition that everyone should use to filter out nuclei that
	# do not qualify for this study
	def doesQualify(self, areaConsidered,areaMin,areaMax, circConsidered,circMin,circMax):
		if (circConsidered == True and (self.Circularity < circMin or self.Circularity > circMax)):
			return False;
		if (areaConsidered == True and (self.Area < areaMin or self.Area > areaMax)):
			return False;
		return True;
