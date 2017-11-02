This is a repository with work-in-progress scripts to carry on proper
measurements on time-lapse 2D wrapped/projected images obtained with
the ImSAnE: https://www.nature.com/nmeth/journal/v12/n12/full/nmeth.3648.html

The wrapped images (embeddings in the original ImSAnE terminology) are 2D
images that actually display a particular surface, just like traditional
map view on the Earth shows the whole globe in one 2D image. Such 2D
images must inevitably include a certain kind of distortions in a real
geometry of pixels, e.g. 5 pixel distance is likely to represent different
real distance depending on where in the wrapped image this distance is
measured, or area that one pixel represents is similarly position dependent.

In such circumstances (non-homogeneous geometry of pixels), however, the
standard image processing methods cannot be used directly. While ImSAnE
offers methods to carry on proper measurements of real physical quantities
on the wrapped images, we found that for some the image processing of the
wrapped images is easier done in Fiji. 

This repository then acts as a collection of tools (one tool per one
folder of this repository) in the forms of Fiji plug-ins, Fiji scripts, or
Matlab scripts that together allow to carry on certain correct(ed)
measurements on the wrapped images.

Note the number prefix in folder names. One should, ideally at first,
export relevant data from ImSAnE/Matlab environment right after the
wrapping of images is done. This can be achieved by running content of the
Matlab script (extension .m). Second, carry on image analysis inside Fiji
with the Jython scripts (extension .py) on the wrapped images with proper
length/area information utilized. If VolumeManager is used for ROI-based
manual segmentation of volumes, one can export the ROIs from the
VolumeManager (use the version found in the attached .jar file) back into
ImSAnE/Matlab and calculate therein proper perimeters of the exported ROIs.


Contact: Vladimír Ulman, ulman na mpi-cbg.de
