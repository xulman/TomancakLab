# Adding textual time scale and user annotation into images

This folder contains one [Fiji](fiji.sc) script that can render time scale and user annotation into time-lapse 2D images.

The time scale is read out from a user given text file. This file needs to contain two columns, time values and frame indices.
The script scans the file and prints the time information into every frame that is discovered in the text file.
This way, one may print time stamps into irregularly sampled images, or select subset of frames for printing the time stamps.
It is assumed that time stamps are floating point numbers that can be printed in two-digits-separator-two-digits format (00.00).

The user annotation is fixed text defined via the script dialog. This text is not varying between frames.
It is always printed into the same frames that are used for time scale printing.
If empty text is provided for the annotation, nothing is printed obviously.

The images has to be in the form of a 3D stack, that is the images are logically a 2D+t sequence.

# How to use the script

Considering the image shown below, one needs to secure the following steps:
* Open the time-lapse image as a 3D stack in Fiji (denoted as *step 1.*)
* Prepare the text image with time scales and frame indicies (denoted as *step 2.*)
* Choose font, font style and size with the Text Tool icon (denoted as *step 3.*)
* Choose font color with the ColorPicker icon
* Open the script with Fiji and run it
* The script will open a dialog (denoted as *step 4.*):
  * The position of bottom-left corner the time stamp must be defined
  * Define prefix that is printed always before the time stamp itself, or leave empty
  * Choose the text file with time stamps and separator of digits
  * Define postfix that is printed always behind the time stamp itself, or leave empty
  * The position of bottom-left corner the annotation may be defined
  * Define the fixed annotation text, or leave empty

![How to use figure](https://github.com/xulman/ImSAnE-Fiji/raw/master/7_putLabels/README_figure.png)


# Example of text file with time values and frame indices

```
first line is ignored
\t3.5\t1\t
\t3.9\t2\t
\t4.6\t3\t
```

This text file would annotate 3 frames in the image stack, in particular the 1st, 2nd and 3rd slice of the stack.
The stack may, however, contain more slices -- they'd be left untouched. The time values inserted would be `03.50`, `03.90`
and `04.60`. The `\t` denotes a tab-space. Note that the lines (except for the first one) must end with tab-space.
