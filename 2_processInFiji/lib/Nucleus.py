import math

# this section adds a folder, in which this very script is living,
# to the current search paths so that we can import our "library script"
import sys.path
import os.path
import inspect
ScriptsRoot = os.path.dirname(os.path.dirname(sys.path[0]))+os.sep+"scripts"
ThisFile    = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.append(ScriptsRoot+os.sep+ThisFile)
sys.path.append(ThisFile)

# import our "library scripts"
from properMeasurements import *


class Nucleus:

	def __init__(self,Color,Pixels,ip,realSizes,realCoords):
		# stringy label of the nuclei
		self.Color = Color

		# a scalar value to be used in chooseNuclei.drawChosenNucleiValue(),
		# one may save here an arbitrary visualization hint for the nuclei drawing
		self.DrawValue = 1

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

		# list of offsets of pixels that make up boundary of this nuclei (nuclei mask)
		self.EdgePixels = []

		# (approximate) length of the boundary in microns
		self.EdgeLength = 0.0

		# shortcut to the pixel values
		i = ip.getPixels()
		w = ip.getWidth()

		# integer label of the nuclei
		self.Label = i[w*Pixels[0][1] + Pixels[0][0]]
		thisColor = self.Label

		# offsets of pixels just outside this nucleus
		self.outterBgEdge = set()

		# set of labels touching this nuclei (component),
		# initially empty -> use setNeighborsList() to have it filled
		self.NeighIDs = set()

		# sequential scan through the boundary pixels:
		# (to be able to smooth out the boundary line consequently)
		#
		# 1) determine boundary pixels and store them apart
		#    (now in self.EdgePixels)
		# 2) replace the "for" cycle just below with this pattern:
		#    - consider only self.EdgePixels
		#    - for current pixel, scan its 4-neig for next pixel
		#      and choose the one that is not the previous pixel
		#    - if none found, scan 8-neig for next pixel
		#      and choose the one that is not the previous pixel
		#    - make the chosen one the current pixel and do cycle body

		# 1) determine boundary pixels first
		for pix in Pixels:
			# pixel offset within the image
			o = w*pix[1] + pix[0]

			try:
				ColorAbove = i[ o-w ]
			except:
				ColorAbove = -1

			try:
				ColorLeft = i[ o-1 ]
			except:
				ColorLeft = - 1

			#thisColor = i[o]

			try:
				ColorRight = i[ o+1 ]
			except:
				ColorRight = -1

			try:
				ColorBelow = i[ o+w ]
			except:
				ColorBelow = -1

			if thisColor != ColorLeft or thisColor != ColorAbove or thisColor != ColorRight or thisColor != ColorBelow:
				# found border-forming pixel, enlist it
				self.EdgePixels.append(o)

		# length of the boundary in pixel
		self.EdgeSize = len(self.EdgePixels)


		# 2) establish the polygon boundary by scanning edge pixels sequentially
		o = self.EdgePixels[0]  # offset of the currently examined pixel
		po = o                  # offsets of the two previously examined pixels
		ppo = o
		pix = [0,0]             # aux coordinate buffer


		# stop criterion: backup the starting point
		veryO = o

		# stop criterion: emergency stop counter
		cntr = 0
		cntrStop = self.EdgeSize

		keepSweeping = True
		while keepSweeping:
			# pixel coords within the image (opposite to: o = w*pix[1] + pix[0])
			pix[1] = int(o/w)
			pix[0] = o - w*pix[1]

			# mimics 2D 4-neighbor erosion:
			# encode which neighbors are missing, and how many of them
			missNeig = 0
			cnt = 0;

			if thisColor != i[ o-w ]:
				missNeig += 2
				cnt += 1
			if thisColor != i[ o-1 ]:
				missNeig += 1
				cnt += 1
			if thisColor != i[ o+1 ]:
				missNeig += 4
				cnt += 1
			if thisColor != i[ o+w ]:
				missNeig += 8
				cnt += 1

			# Marching-cubes-like determine configuration of the border pixel,
			# and guess an approximate proper length of the boundary this pixels co-establishes

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
				if missNeig&1:
					# vertical boundary
					coords = [ [pix[0]-0.5,pix[1]-0.5] , [pix[0]-0.5,pix[1]] , [pix[0]-0.5,pix[1]+0.5] ]
				elif missNeig&4:
					# vertical boundary
					coords = [ [pix[0]+0.5,pix[1]-0.5] , [pix[0]+0.5,pix[1]] , [pix[0]+0.5,pix[1]+0.5] ]
				elif missNeig&2:
					# horizontal boundary
					coords = [ [pix[0]-0.5,pix[1]-0.5] , [pix[0],pix[1]-0.5] , [pix[0]+0.5,pix[1]-0.5] ]
				else:
					# horizontal boundary
					coords = [ [pix[0]-0.5,pix[1]+0.5] , [pix[0],pix[1]+0.5] , [pix[0]+0.5,pix[1]+0.5] ]

			if cnt == 2:
				# two neighbors -> we're either a corner, or boundary is 1px thick
				if missNeig&5 == 5 or missNeig&10 == 10:
					# 1px thick boundary
					if missNeig&5 == 5:
						# 1px thick vertical boundary
						coords = [ [pix[0]-0.5,pix[1]-0.5] , [pix[0]-0.5,pix[1]] , [pix[0]-0.5,pix[1]+0.5] ]
						self.EdgeLength += properLength(coords,realCoords)
						coords = [ [pix[0]+0.5,pix[1]-0.5] , [pix[0]+0.5,pix[1]] , [pix[0]+0.5,pix[1]+0.5] ]
					else:
						# 1px thick horizontal boundary
						coords = [ [pix[0]-0.5,pix[1]-0.5] , [pix[0],pix[1]-0.5] , [pix[0]+0.5,pix[1]-0.5] ]
						self.EdgeLength += properLength(coords,realCoords)
						coords = [ [pix[0]-0.5,pix[1]+0.5] , [pix[0],pix[1]+0.5] , [pix[0]+0.5,pix[1]+0.5] ]

					# will return to this pixel again (on the way back),
					# need therefore more steps (this cycle iterations)...
					cntrStop = cntrStop+1
				else:
					# missing neighbors are "neighbors" to each other too -> we're a corner
					if missNeig&6 == 6 or missNeig&9 == 9:
						# we're top-right corner, or bottom-left corner
						coords = [ [pix[0]-0.5,pix[1]-0.5] , [pix[0],pix[1]] , [pix[0]+0.5,pix[1]+0.5] ]

					if missNeig&12 == 12 or missNeig&3 == 3:
						# we're bottom-right corner, or top-left corner
						coords = [ [pix[0]-0.5,pix[1]+0.5] , [pix[0],pix[1]] , [pix[0]+0.5,pix[1]-0.5] ]

			if cnt == 3:
				# three neighbors -> we're "a blob or a spike" popping out from a straight boundary...
				if missNeig&7 == 7:
					# have only a neighbor below
					coords = [ [pix[0]-0.5,pix[1]+0.5] , [pix[0],pix[1]] , [pix[0]+0.5,pix[1]+0.5] ]

				if missNeig&11 == 11:
					# have only a neighbor right
					coords = [ [pix[0]+0.5,pix[1]-0.5] , [pix[0],pix[1]] , [pix[0]+0.5,pix[1]+0.5] ]

				if missNeig&13 == 13:
					# have only a neighbor above
					coords = [ [pix[0]-0.5,pix[1]-0.5] , [pix[0],pix[1]] , [pix[0]+0.5,pix[1]-0.5] ]

				if missNeig&14 == 14:
					# have only a neighbor left
					coords = [ [pix[0]-0.5,pix[1]-0.5] , [pix[0],pix[1]] , [pix[0]-0.5,pix[1]+0.5] ]

			if cnt == 4:
				# four neighbors -> we're an isolated pixel.. should not happen! as we did CCA to
				# obtain this patches, so one patch/nucleus is one connected component
				#
				#coords = [ [pix[0]-0.5,pix[1]] , [pix[0],pix[1]+0.5] , [pix[0]+0.5,pix[1]] , [pix[0],pix[1]-0.5] , [pix[0]-0.5,pix[1]] ]
				cntrStop = cntrStop-1

			# calculate the proper length of the local boundary by sweeping
			# typically through a neighbor,myself,neighbor
			self.EdgeLength += properLength(coords,realCoords)

			# enlist background pixels surrounding this edge/border pixel
			for x in [-w-1,-w,-w+1, -1,1, +w-1,+w,+w+1]:
				if i[o+x] == 0:
					self.outterBgEdge.add(o+x)

			# find adjacent edge pixel
			for n in [ -w, -1,1, w, -w-1, -w+1, w-1, w+1 ]:
				no = n+o # new examined pixel
				if no in self.EdgePixels and no != po and no != ppo:
					ppo = po
					po = o
					o = no
					break

			# test if enough has been swept....
			cntr = cntr+1
			if o == veryO or cntr >= cntrStop:
				keepSweeping = False

		# circularity: higher value means higher circularity
		self.Circularity = (self.Area * 4.0 * math.pi) / (self.EdgeLength * self.EdgeLength)

		# shape factor: perimeter / sqrt(area)
		self.ShapeFactor = self.EdgeLength / math.sqrt(self.Area)


	def setNeighborsList(self, img):
		setNeighborsList(img.getProcessor().getPixels(), img.getWidth())

	def setNeighborsList(self, i,w):
		self.NeighIDs = set([self.Label])

		# iterate over all just-outside-boundary pixels,
		# and check their surrounding values
		for oo in self.outterBgEdge:
			for x in [-w-1,-w,-w+1, -1,1, +w-1,+w,+w+1]:
				if i[oo+x] > 0:
					self.NeighIDs.add(i[oo+x])
		self.NeighIDs.remove(self.Label)


	# the same condition that everyone should use to filter out nuclei that
	# do not qualify for this study
	def doesQualify(self, areaConsidered,areaMin,areaMax, circConsidered,circMin,circMax):
		if (circConsidered == True and (self.Circularity < circMin or self.Circularity > circMax)):
			return False;
		if (areaConsidered == True and (self.Area < areaMin or self.Area > areaMax)):
			return False;
		return True;
