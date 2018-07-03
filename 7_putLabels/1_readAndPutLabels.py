#@ boolean (label="Double click 'TextTool' to choose font") notUsed1
#@ boolean (label="Double click 'ColorPicker' to choose color") notUsed2
#@ int (label="bottom left corner [pixels], X=") X
#@ int (label="bottom left corner [pixels], Y=") Y
#@ String (label="prefix text=", required=False) labelsPrefix
#@ File (label="file with labels") labelsFile
#@ String (label="postfix text=", required=False) labelsPostfix
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
	# sweep through the image stack
	for l in range(len(labels)):
		image.setSlice(labels[l][0])

		# set font-info for the current slice
		ip = image.getProcessor()
		ip.setFont(font)
		ip.setColor(color)

		# render the text to the current slice
		ip.moveTo(X, Y)
		msg = labelsPrefix+str(labels[l][1])+labelsPostfix

		ip.drawString(msg)
		print "drawing >"+msg+"< into slice >"+str(labels[l][0])+"<"


main()
#image.updateAndDraw()
print "done."
