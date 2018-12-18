//upscale close to the original size
run("Scale...", "x=2 y=2 interpolation=None average  create title=upScaled.tif");

//shift values to make it compatible with the scripts,
//that is: 0 - background, 1 - nuclei, 2 - membranes
run("Add...", "value=1");

//run the main script,
//and check instance-segmentation image for holes, jagged boundaries or just slit segments

//run testPseudoClosing.py if neccesary to correct the instance-segmentation image,
//and convert back to a variant that is again compatible with the scripts (see above)
setThreshold(0, 0);
run("Convert to Mask");
run("Divide...", "value=255");
run("Add...", "value=1");