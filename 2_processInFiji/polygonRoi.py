from ij import IJ
from ij import ImagePlus
from ij.process import FloatPolygon


# given: x larger is right; y smaller is up
# CCW
#xArray = [10.5, 15.5, 14.5, 11.5]
#yArray = [20  , 20  , 10  , 10  ]
#
# CW
xArray = [11.5, 14.5, 15.5, 10.5]
yArray = [10  , 10  , 20  , 20  ]
#
# conclusion:
# clockwise-ness does not matter

# hour-glass shape, still works fine
#xArray = [11.5, 15.5,14.5,  10.5]
#yArray = [10  , 20  ,10  ,  20  ]

p = FloatPolygon(xArray,yArray)
print("polygon perimeter: "+str(p.getLength(False)))


for y in range(8,22):
	for x in range(8,18):
		#if p.contains(float(x),float(y)):
		if p.contains(x,y):
			print("["+str(x)+","+str(y)+"] is inside")

