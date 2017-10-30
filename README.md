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

The folder names contains a suffix: 'M' stands for Matlab, 'F' stands for
Fiji, order matters. The meaning for '_MF', for example, is that one needs
first run some Matlab scripts (typically to export necessary data), and
continue afterwads with some Fiji processing. In the case of '_MFM', one
has to return to Matlab again after the Fiji processing to complete the
calculations.


Contact: Vladimír Ulman, ulman na mpi-cbg.de
