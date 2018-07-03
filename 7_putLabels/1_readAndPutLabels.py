#@ boolean (label="Double click 'TextTool' to choose font") notUsed1
#@ boolean (label="Double click 'ColorPicker' to choose color") notUsed2
#@ int (label="bottom left corner [pixels], X=") X
#@ int (label="bottom left corner [pixels], Y=") Y
#@ File (label="file with labels") labelsFile

from ij import IJ
from ij.gui import Toolbar
from ij.gui import TextRoi
from java.awt import Font

# get info about the preferred font, font style/size, color
font = Font(TextRoi.getFont(), TextRoi.getStyle(), TextRoi.getSize());
color = Toolbar.getForegroundColor()

# get reference to the image
image = IJ.getImage()

def main():
	# sweep through the image stack
	for z in range(1,1+image.getStackSize()):
		image.setSlice(z)

		# set font-info for the current slice
		ip = image.getProcessor()
		ip.setFont(font)
		ip.setColor(color)

		# render the text to the current slice
		ip.moveTo(X, Y)
		ip.drawString("hi "+str(z))


main()
#image.updateAndDraw()
print "done."
