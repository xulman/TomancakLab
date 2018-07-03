#@ boolean (label="Double click 'TextTool' icon to choose font.",     description="This checkbox is ignored.") notUsed1
#@ boolean (label="Double click 'ColorPicker' icon to choose color.", description="This checkbox is ignored.") notUsed2

#@ int (label="X position of Time [pixels], X=", description="Should fit into the image.") X
#@ int (label="Y position of Time [pixels], Y=", description="Should fit into the image.") Y
#@ String (label="Time prefix", required=False,  description="Time information is composed from prefix, timestamp with the given separator and postfix.") labelsPrefix
#@ File (label="file with Time stamps",           description="Time information is composed from prefix, timestamp with the given separator and postfix.") labelsFile
#@ String (label="Time postfix", required=False, description="Time information is composed from prefix, timestamp with the given separator and postfix.") labelsPostfix

#@ int (label="X position of Annotation [pixels], X=", description="Should fit into the image.") Xt
#@ int (label="Y position of Annotation [pixels], Y=", description="Should fit into the image.") Yt
#@ String (label="Annotation text", required=False, description="This text will appear in every slice of the stack.") textMsg

labelsFile = labelsFile.getAbsolutePath()
if labelsPrefix == None:
	labelsPrefix = ""
if labelsPostfix == None:
	labelsPostfix = ""

from ij import IJ
from ij.gui import Toolbar
from ij.gui import TextRoi
from java.awt import Font


def readLabelsTxtFile(fn):
	# output list (yet empty)
	labels = []

	# open the image and ignore the first line
	f = open(fn,"r")
	line = f.readline()

	while True:
		# read next line (and replace ',' with '.')
		line = f.readline().replace(",",".")

		if len(line) < 3:
			return labels

		# remove all odd positions (which happen to zero-valued char)
		cleanline = ""
		odd = True
		for l in line:
			odd ^= True
			if odd:
				cleanline += l

		line = cleanline

		# find "separators" between the columns
		ws1 = line.find("\t",2)
		ws2 = line.find("\t",ws1+1)

		# extract the numbers from both columns
		label = float(line[1:ws1])
		time  =   int(line[ws1+1:ws2])

		labels.append([time,label])

	f.close()
	# the function exists from inside the while loop...


# get info about the preferred font, font style/size, color
font = Font(TextRoi.getFont(), TextRoi.getStyle(), TextRoi.getSize());
color = Toolbar.getForegroundColor()

# get reference to the image
image = IJ.getImage()

labels = readLabelsTxtFile(labelsFile)

def main():
	# sweep through the time points from the file
	for l in range(len(labels)):
		z = labels[l][0]

		# check the time point is within the range of the opened image
		if z > 0 and z <= image.getStackSize():
			image.setSlice(z)

			# set font-info for the current slice
			ip = image.getProcessor()
			ip.setFont(font)
			ip.setColor(color)

			# render the text to the current slice
			ip.moveTo(X, Y)
			msg = labelsPrefix+str(labels[l][1])+labelsPostfix

			ip.drawString(msg)
			print "drawing >"+msg+"< into slice >"+str(z)+"<"

			# draw also the fixed additional text/annotation
			if textMsg != None and len(textMsg) > 0:
				ip.moveTo(Xt,Yt)
				ip.drawString(textMsg)
				print "drawing >"+textMsg+"< into slice >"+str(z)+"<"


main()
#image.updateAndDraw()
print "done."
