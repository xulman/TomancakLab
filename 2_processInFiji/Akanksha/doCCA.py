import numpy as np
import sys
from skimage import measure
from tifffile import imread
from tifffile import imsave

if len(sys.argv) != 3:
	print("two arguments expect: path_to_input_image  path_to_output_image")
	sys.exit(0)


# read input image
i = imread(sys.argv[1])

# connected component analysis + output type conversion
c = measure.label(i, background=0, connectivity=1)
c = c.astype(np.uint16)

# save output image
imsave(sys.argv[2],c)
