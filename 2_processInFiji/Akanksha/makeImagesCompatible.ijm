//upscale close to the original size
//
//tp   0: 802 x 1166
run("Scale...", "x=- y=- width=802 height=1166 interpolation=None average create title=upScaled.tif");
run("Add...", "value=1");

//tp 130: 795 x 1222
run("Scale...", "x=- y=- width=795 height=1222 interpolation=None average create title=upScaled.tif");
run("Add...", "value=1");

//tp 190: 809 x 1210
run("Scale...", "x=- y=- width=809 height=1210 interpolation=None average create title=upScaled.tif");
run("Add...", "value=1");

//tp 215: 821 x 1220
run("Scale...", "x=- y=- width=821 height=1220 interpolation=None average create title=upScaled.tif");
run("Add...", "value=1");

//tp 270: 821 x 1226
run("Scale...", "x=- y=- width=821 height=1226 interpolation=None average create title=upScaled.tif");
run("Add...", "value=1");

//tp 400: 826 x 1228
run("Scale...", "x=- y=- width=826 height=1228 interpolation=None average create title=upScaled.tif");
run("Add...", "value=1");


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
