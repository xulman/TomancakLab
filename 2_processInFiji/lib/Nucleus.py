import math
import copy
from ij.process import FloatPolygon

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

		eightNH     = [-w-1,-w,-w+1, -1,1, +w-1,+w,+w+1]
		eightNHdist = [   2, 1,   2,  1,1,    2, 1,   2] #L0-dist to neighs

		# integer label of the nuclei
		self.Label = i[w*Pixels[0][1] + Pixels[0][0]]
		thisColor = self.Label

		# offsets of pixels just outside this nucleus
		self.outterBgEdge = set()
		self.outterBgEdgeCW = []

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

		coords = []             # list of polygon vertices that encloses the nucleus

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
					coords.append( [pix[0]-0.5,pix[1]-0.5] )
					coords.append( [pix[0]-0.5,pix[1]] )
				elif missNeig&4:
					# vertical boundary
					coords.append( [pix[0]+0.5,pix[1]+0.5] )
					coords.append( [pix[0]+0.5,pix[1]] )
				elif missNeig&2:
					# horizontal boundary
					coords.append( [pix[0]+0.5,pix[1]-0.5] )
					coords.append( [pix[0],pix[1]-0.5] )
				else:
					# horizontal boundary
					coords.append( [pix[0]-0.5,pix[1]+0.5] )
					coords.append( [pix[0],pix[1]+0.5] )

			if cnt == 2:
				# two neighbors -> we're either a corner, or boundary is 1px thick
				if missNeig&5 == 5 or missNeig&10 == 10:
					# 1px thick boundary
					if missNeig&5 == 5:
						# 1px thick vertical boundary
						if po < o:
							coords.append( [pix[0]-0.5,pix[1]-0.5] )
							coords.append( [pix[0]-0.5,pix[1]] )
						else:
							coords.append( [pix[0]+0.5,pix[1]+0.5] )
							coords.append( [pix[0]+0.5,pix[1]] )
					else:
						# 1px thick horizontal boundary
						# po % w is position on x-axis
						if po%w > o%w:
							coords.append( [pix[0]+0.5,pix[1]+0.5] )
							coords.append( [pix[0]    ,pix[1]+0.5] )
						else:
							coords.append( [pix[0]-0.5,pix[1]-0.5] )
							coords.append( [pix[0]    ,pix[1]-0.5] )

					# will return to this pixel again (on the way back),
					# need therefore more steps (this cycle iterations)...
					cntrStop = cntrStop+1
				else:
					# missing neighbors are "neighbors" to each other too -> we're a corner
					if missNeig&6 == 6:
						# we're top-right corner
						coords.append( [pix[0]+0.5,pix[1]+0.5] )
						coords.append( [pix[0],pix[1]] )
					elif missNeig&9 == 9:
						# we're bottom-left corner
						coords.append( [pix[0]-0.5,pix[1]-0.5] )
						coords.append( [pix[0],pix[1]] )

					if missNeig&12 == 12:
						# we're bottom-right corner
						coords.append( [pix[0]-0.5,pix[1]+0.5] )
						coords.append( [pix[0],pix[1]] )
					elif missNeig&3 == 3:
						# we're top-left corner
						coords.append( [pix[0]+0.5,pix[1]-0.5] )
						coords.append( [pix[0],pix[1]] )

			if cnt == 3:
				# three neighbors -> we're "a blob or a spike" popping out from a straight boundary...
				if missNeig&7 == 7:
					# have only a neighbor below
					coords.append( [pix[0]+0.5,pix[1]+0.5] )
					coords.append( [pix[0],pix[1]] )

				if missNeig&11 == 11:
					# have only a neighbor right
					coords.append( [pix[0]+0.5,pix[1]-0.5] )
					coords.append( [pix[0],pix[1]] )

				if missNeig&13 == 13:
					# have only a neighbor above
					coords.append( [pix[0]-0.5,pix[1]-0.5] )
					coords.append( [pix[0],pix[1]] )

				if missNeig&14 == 14:
					# have only a neighbor left
					coords.append( [pix[0]-0.5,pix[1]+0.5] )
					coords.append( [pix[0],pix[1]] )

			if cnt == 4:
				# four neighbors -> we're an isolated pixel.. should not happen! as we did CCA to
				# obtain this patches, so one patch/nucleus is one connected component
				#
				#coords = [ [pix[0]-0.5,pix[1]] , [pix[0],pix[1]+0.5] , [pix[0]+0.5,pix[1]] , [pix[0],pix[1]-0.5] , [pix[0]-0.5,pix[1]] ]
				cntrStop = cntrStop-1

			# enlist background pixels surrounding this edge/border pixel into outterBgEdge,
			# enlist CW-ordered outter pixels of 'o' into outterBgEdgeCW
			xBestDist = 5
			xBestIdx  = 0
			for n in range(len(eightNH)):
				x = o + eightNH[n]
				if i[x] == 0:
					if eightNHdist[n] <= xBestDist and not x in self.outterBgEdge:
						xBestDist = eightNHdist[n]
						xBestIdx  = x

					self.outterBgEdge.add(x)

			if xBestDist < 5:
				self.outterBgEdgeCW.append(xBestIdx)

			# find adjacent edge pixel
			if cntr == 0:
				# first run, find neighbor in CCW direction
				# first: vector from o towards nuclei interior
				# second: search neighbor pixels that are CCW from the first vector

				# first vector:
				fvx = 0
				fvy = 0
				do = [ -w, -1, 1, w, -w-1, -w+1, w-1, w+1 ]
				dx = [  0, -1, 1, 0,   -1,    1,  -1,   1 ]
				dy = [ -1,  0, 0, 1,   -1,   -1,   1,   1 ]
				for n in range(len(do)):
					if thisColor == i[ do[n]+o ]:
						fvx += dx[n]
						fvy += dy[n]
				# (fvx, fvy) points inward nuclei
				# (fvy,-fvx) is CCW rotated -- for angular inspection w.r.t. (svx,svy)

				# examine second vectors:
				for n in do:
					no = n+o # new examined pixel
					svx =     no%w  -     o%w
					svy = int(no/w) - int(o/w)
					ang = fvy*svx - fvx*svy

					if no in self.EdgePixels and ang < 0:
						o = no
						break
			else:
				# any next run, find neighbor not the same as the previous one(s)
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

		# finish the loop...
		coords.append( coords[0] )
		self.Coords = coords

		# calculate the proper length of the local boundary by sweeping
		# typically through a neighbor,myself,neighbor
		self.EdgeLength += properLength(coords,realCoords)

		if len(coords) < 20:
			print("nucleus #"+str(thisColor)+" has suspiciously short circumference polygon ("+str(len(coords))+" vertices)")

		if len(coords) != 2*self.EdgeSize+1:
			print("nucleus #"+str(thisColor)+" has unexpected length of circumference polygon ("+str(len(coords))+" vertices, should be "+str(2*self.EdgeSize+1)+")")

		self.updateCircularityAndSA()


	def reshapeNucleusWithStraightenedBoundary(self, img):
		self.reshapeNucleusWithStraightenedBoundary(img.getProcessor().getPixels(), img.getWidth())

	def reshapeNucleusWithStraightenedBoundary(self, i,w):
		# now, scan the vicinities of the self.outterBgEdgeCW and detect junction-points
		# neighbors that define vicinity of interest
		jn = [ -2*w-2, -2*w-1, -2*w, -2*w+1, -2*w+2,
		       -1*w-2,                       -1*w+2,
		           -2,                           +2,
		       +1*w-2,                       +1*w+2,
		       +2*w-2, +2*w-1, +2*w, +2*w+1, +2*w+2 ]

		# offsets of the junction-points, but in two flavours:
		# truly and only the (inner) junction points - that is such boundary points
		# that are surrounded by at least three different labels (that is three different
		# nuclei/cells)
		self.CoordsInnerJunctions = []
		#
		# all important boundary-shaping points: includes the self.CoordsInnerJunctions plus
		# points on the "outside of the nuclei/cell" -- points that saw only one (mine) label;
		# these are typically on the outskirts of the (unwrapped) image
		self.CoordsJunctions = []

		# also an "inner" neighborhood -- that is "instantiated" around
		# every background pixel (from self.outterBgEdgeCW) that comes
		# out from the 'jn' array -- to look for absence of any pixel
		# from this nucleus --> only then the "junction" pixel is found
		nn = [ -w-1, -w, -w+1, -1, +1, w-1, w, w+1 ]

		# over all outter edge pixels...
		# (essentially a nearby/nucleus-touching background pixels)
		for oo in self.outterBgEdgeCW:
			# ...and over the surroundings of every outter edge pixel
			seenOtherNucleiAtAll = False
			for ojn in jn:
				ooo = oo+ojn #Other Outter edge pixel Offset

				if ooo >= 0 and ooo < len(i) and i[ooo] == i[oo]:
					# found another background pixel, examine its neighborhood
					seenMyNuclei = False
					seenOtherNuclei = False

					for n in nn:
						if ooo+n >= 0 and ooo+n < len(i) and i[ooo+n] != i[oo]:
							# found some nucleus pixel around the current 'ooo' pixel
							if i[ooo+n] == self.Label:
								seenMyNuclei = True
							else:
								seenOtherNuclei = True
								seenOtherNucleiAtAll = True

					if seenMyNuclei == False and seenOtherNuclei == True:
						self.CoordsJunctions.append(oo)
						self.CoordsInnerJunctions.append(oo)
						break

			if seenOtherNucleiAtAll == False:
				self.CoordsJunctions.append(oo)

		# now, update the self.Coords - let it go through pixel centres
		self.Coords = []
		for o in self.CoordsJunctions:
			y = int(o/w)
			x = o - y*w
			self.Coords.append( [x,y] )
		# finish the loop...
		self.Coords.append( self.Coords[0] )


	def updateCircularityAndSA(self):
		# circularity: higher value means higher circularity
		self.Circularity = (self.Area * 4.0 * math.pi) / (self.EdgeLength * self.EdgeLength)

		# shape factor: perimeter / sqrt(area)
		self.ShapeFactor = self.EdgeLength / math.sqrt(self.Area)


	def setNeighborsList(self, img):
		self.setNeighborsList(img.getProcessor().getPixels(), img.getWidth())

	def setNeighborsList(self, i,w):
		self.NeighIDs = set([self.Label])

		# iterate over all just-outside-boundary pixels,
		# and check their surrounding values
		for oo in self.outterBgEdge:
			for x in [-w-1,-w,-w+1, -1,1, +w-1,+w,+w+1]:
				if i[oo+x] > 0:
					self.NeighIDs.add(i[oo+x])
		self.NeighIDs.remove(self.Label)


	def smoothPolygonBoundary(self, smoothSpan, smoothSigma):
		if smoothSpan < 1 or smoothSigma <= 0:
			return

		weights = [ math.exp(-0.5 * i*i / (smoothSigma*smoothSigma)) for i in range(smoothSpan+1) ]

		wSum = -weights[0]
		for w in weights:
			wSum += 2.0 * w

		coordsOrig = copy.copy(self.Coords)
		coordsLen = len(self.Coords)

		for i in range(coordsLen):
			x = weights[0] * coordsOrig[i][0]
			y = weights[0] * coordsOrig[i][1]

			for j in range(1,smoothSpan+1):
				x += weights[j] * ( coordsOrig[(i-j) %coordsLen][0] + coordsOrig[(i+j) %coordsLen][0] )
				y += weights[j] * ( coordsOrig[(i-j) %coordsLen][1] + coordsOrig[(i+j) %coordsLen][1] )

			self.Coords[i][0] = x / wSum
			self.Coords[i][1] = y / wSum


	# the same condition that everyone should use to filter out nuclei that
	# do not qualify for this study
	def doesQualify(self, areaConsidered,areaMin,areaMax, circConsidered,circMin,circMax):
		if (circConsidered == True and (self.Circularity < circMin or self.Circularity > circMax)):
			return False;
		if (areaConsidered == True and (self.Area < areaMin or self.Area > areaMax)):
			return False;
		return True;


	# updates the Pixels, Area, Size, CentreX and CentreY attributes of this object
	# based on the current content of self.Coords, and the given 'realSizes' map
	def getBoundaryInducedArea(self,realSizes):
		# re-shape the self.Coords to make it usable for the FloatPolygon class,
		# and to determine bbox around the current nucleus at the same time
		minX = self.Coords[0][0]
		maxX = self.Coords[0][0]
		minY = self.Coords[0][1]
		maxY = self.Coords[0][1]

		xVertices = []
		yVertices = []

		for c in self.Coords:
			minX = min(minX,c[0])
			maxX = max(maxX,c[0])

			minY = min(minY,c[1])
			maxY = max(maxY,c[1])

			xVertices.append(c[0])
			yVertices.append(c[1])

		# round and "integerify" the bounding box bounds
		minX = int(math.floor(minX))
		maxX = int(math.ceil( maxX))

		minY = int(math.floor(minY))
		maxY = int(math.ceil( maxY))

		p = FloatPolygon(xVertices,yVertices)

		self.Pixels = []
		for y in range(minY,maxY+1):
			for x in range(minX,maxX+1):
				if p.contains(x,y):
					self.Pixels.append([x,y])

		# update the area calculation
		# object area in squared microns
		self.Area = 0.0
		# object area in pixel number
		self.Size = len(self.Pixels)

		# geometric centre in pixel coordinates
		self.CentreX = 0.0
		self.CentreY = 0.0

		# calculate real size and geometrical centre
		for pix in self.Pixels:
			self.Area += realSizes[pix[0]][pix[1]]
			self.CentreX += pix[0]
			self.CentreY += pix[1]

		# finish calculation of the geometrical centre
		self.CentreX /= len(self.Pixels)
		self.CentreY /= len(self.Pixels)
