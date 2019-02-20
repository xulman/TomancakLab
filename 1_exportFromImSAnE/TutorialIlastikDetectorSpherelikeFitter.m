%% ImSAnE: Tutorial with Ilastik Detector and Spherelike Fitter
% 
% Sample data: Insect embryo
%
% In this tutorial we detect the embryos apical surface using Ilastik and
% read the prediction file and generate a point cloud using the ilastik
% detector, fit a spherelike surface, generate a surface of interest
% and pullback the image data to various charts.
%
% This an example of how to detect and fit what we call spherelike surfaces,
% where the surface can be described as a slowly varying function of a
% preferred axis, which we call the z-axis. 
%
% Here is how to access the documentation of detectors and fitters that are
% introduced in this tutorial

%%
% 
doc surfaceDetection.ilastikDetector


%% Initialize ImSAnE project
%
% We start by clearing the memory and closing all figures.
%
clear all; close all;
%%
%
% Setup a working directory for the project, where extracted surfaces,
% metadata and debugging output will be stored. Also specify the directory
% containing the data. 
%
[scriptPath,~,ext] = fileparts(matlab.desktop.editor.getActiveFilename);

dataDir    = '/mnt/projects/ulman/p_Mangal/imsane/s1e2'; %fullfile(scriptPath, 'rawData');
projectDir = fullfile(scriptPath, 'projectFiles');


xp = project.Experiment(projectDir, dataDir);
cd(dataDir)

fileMeta                 = struct();
fileMeta.dataDir         = dataDir;
fileMeta.filenameFormat  = 't%02d.tif'; %'Time%06d_8bit_bin2.tif'; % for full data sample use Time000000.tif
fileMeta.nChannels       = 1; % number of channels must be specified for matlab reader to function.
fileMeta.timePoints      = [1:2]; 
fileMeta.stackResolution = [0.38 0.38 0.38];
%fileMeta.stackResolution = [1.0 1.0 1.0];
fileMeta.swapZT          = 0;

expMeta                  = struct();
expMeta.channelsUsed     = 1;
expMeta.channelColor     = 1;
expMeta.description      = 'Vlado is unwrapping';
expMeta.dynamicSurface   = 0;
expMeta.jitterCorrection = 0; 
expMeta.fitTime          = fileMeta.timePoints(1); 
expMeta.detectorType     = 'surfaceDetection.ilastikDetector';
expMeta.fitterType       = 'surfaceFitting.spherelikeFitter'; 
%

xp.setFileMeta(fileMeta);
xp.setExpMeta(expMeta);
%

xp.initNew();

%% Load data for surface detection and rescale to unit aspect ratio

xp.loadTime(1);
xp.rescaleStackToUnitAspect();

%% Detect the surface

myDetectOpts = struct('channel', 1, 'sigma', 2, 'ssfactor', 4,...
            'rmRadialOutliers', 1.5,'thresh',.6,'amin',50,'dildisc',5,...
            'fileName',[xp.fileMeta.dataDir,'/forIlastik'],...
            'foreGroundChannel',2,'zdim',2); 
xp.setDetectOptions(myDetectOpts);
% fileName is the (final) full output name (not a prefix s2* or alike),
% will give out in this case: ...dataDir/s2.h5

%% KEEP PROCESSING SECTIONS UP TO THIS SECTION (INCLUDING THIS SECTION)
xp.detector.prepareIlastik(xp.stack);

%% AFTER ILASTIK, START FROM THIS SECTION BASICALLY ALL THE WAY DOWN,
% CHECK FIT!
% only once the surface has been processed in ilastik can it be identified
% by the detector, which then extracts a point Cloud based on the above
% settings. Do train a classifier, open Ilastik, and follow the
% instructions given on www.ilastik.org (the pixel classifiction workflow 
% desribed at the webpage will be particularly useful for this step:
% http://ilastik.org/documentation/pixelclassification/pixelclassification.html). 
% We recommend to use the backround channel as class one and foregroundChannel 
% as class two, when using the myDetectOpts specified above. Otherwise
% change the foregroundChannel Option appropriately. 
 
xp.detectSurface();


%% Inspect the point cloud in a cross section,
% RUN SEVERAL TIMES WITH DIFFERENT 'x' and '800'

inspectOptions= struct('dimension', 'x', 'value', 800, 'pointCloud', 'b')
xp.detector.inspectQuality(inspectOptions, xp.stack);
% plane cuts the volume at 'dimension'='value', e.g. x=200, z=120
% (original, not-downsampled, coordinates are used!)

%% Inspect pointcloud in 3d
%
% Plot the points on the surface as a three dimensional point cloud.
% The subsampling factor reduces the number of points shown. 
%
ssfactor = 6;
xp.detector.pointCloud.inspect(ssfactor);

%% Fit the surface coarsly to prepare estimate of sample orientation

fitOptions = struct('R',6,'X',4,'Y',4,'e',2,'phase',0,'path',...
                    fullfile(projectDir, 'debugOutput'));
xp.setFitOptions(fitOptions);
xp.fitSurface();
%
% Determine sample orientation and perform fine fit
xp.determineROIfromFit();
fitOptions = struct('R',8,'X',3,'Y',3,'e',1,'phase',0,'shift',0);
xp.setFitOptions(fitOptions);
xp.fitSurface();
%
%% Inspect the fit in a cross section
% RUN SEVERAL TIMES WITH DIFFERENT 'x' and '800'

zval = 600;
Options = struct('dimension','z','value',zval,'pointCloud','b');
xp.fitter.inspectQuality(Options, xp.detector, xp.stack);

%% Inspect the fit over the detection points in a series of cross sections
% viewing params:
dimLabels = ['x','y','z'];
dimChooser = 1;            % 1 = x, 2 = y, 3 = z
dimStep = 5;               % in pixels

inspectOptions = struct('dimension', dimLabels(dimChooser), 'value', 0, 'pointCloud', 'b');

% prealocate structs
%myFrames(1:ceil((xp.fileMeta.stackSize(1)+0.01)/dimStep)) = struct('cdata',[],'colormap',[]);
%frameCnt = 0;

vw = VideoWriter(['pointsInspectionAlong_',dimLabels(dimChooser),'.avi'],'Uncompressed AVI');
open(vw);

% Prepare video of slices scanning the original image
for x = 0:dimStep:xp.fileMeta.stackSize(dimChooser)
    inspectOptions.value=x;

    inspectOptions.pointCloud='b';
    xp.detector.inspectQuality(inspectOptions, xp.stack);

    hold on
    inspectOptions.pointCloud='r';
    xp.fitter.inspectQuality(inspectOptions, xp.detector, xp.stack);
    hold off

    t=text(50,50,[dimLabels(dimChooser),'=',int2str(x)]);
    set(t,'BackgroundColor','w');

    %frameCnt=frameCnt+1;
    %myFrames(frameCnt) = getframe;
    frame = getframe;
    writeVideo(vw,frame);
end

close(vw);
%movie(myFrames,5,1)
%movie2avi(myFrames,['pointsInspectionAlong_',dimLabels(dimChooser),'.avi'],'FPS',4,'COMPRESSION','None')
['done.']

%% Inspect the could point of fitted points in 3D (in red)
% THIS IS NICE COMPARISON OF THE DETECTED AND FITTED SURFACES

fittedPointsCoords = xp.fitter.fittedPoints;
Xcoords=reshape(fittedPointsCoords{1},[],1);
Ycoords=reshape(fittedPointsCoords{2},[],1);
Zcoords=reshape(fittedPointsCoords{3},[],1);

sparsity = 500;
howMuch  = floor(1 * size(Xcoords,1));
plot3(Xcoords(1:sparsity:howMuch), Ycoords(1:sparsity:howMuch), Zcoords(1:sparsity:howMuch), 'r.');

hold

% Inspect the could point of detected points in 3D (in blue)
% Boths plots will be overlaid over each other.
detectedPointsCoords = xp.detector.pointCloud.points;
sparsity2 = floor( size(detectedPointsCoords,1)/howMuch*sparsity );
plot3(detectedPointsCoords(1:sparsity2:end,1), detectedPointsCoords(1:sparsity2:end,2), detectedPointsCoords(1:sparsity2:end,3), 'b.');

hold off

%% Fitted points as a surface plot
redX=20; redY=20;
surf(fittedPointsCoords{1}(1:redX:end,1:redY:end), fittedPointsCoords{2}(1:redX:end,1:redY:end), fittedPointsCoords{3}(1:redX:end,1:redY:end));

%% TODO: export the fitted surface as an image and display it overlaid on
% the original data in BDV...


%% Inspect the bounding box on the sample
%
% draw the bounding box around the sample obtained by determineROIfromFit 
% in 3 different cross-sections through the centre of mass of the data.
%
scale = 100;
subplot(1, 3, 1);
imshow(xp.stack.getSlice('x', xp.currentROI.originp(1)));
view_sec = 'yz';
xp.detector.pointCloud.ROI.drawAxes(view_sec, scale);
xp.detector.pointCloud.ROI.drawROI(view_sec);
subplot(1, 3, 2);
imshow(xp.stack.getSlice('y', xp.currentROI.originp(2)));
view_sec = 'zx';
xp.detector.pointCloud.ROI.drawAxes(view_sec, scale);
xp.detector.pointCloud.ROI.drawROI(view_sec);
subplot(1, 3, 3);
imshow(xp.stack.getSlice('z', xp.currentROI.originp(3)));
view_sec = 'xy';
xp.detector.pointCloud.ROI.drawAxes(view_sec, scale);
xp.detector.pointCloud.ROI.drawROI(view_sec);

%% Normally evolve the fitted surface by shift in pixels
% ONLY IF NECCESARY
%
% Depending on the part of the dataset we want to extract, we may want to 
% displace the surface by shift in the direction of the surface normal.
% Positive values move inwards, negative values outwards.
shift = 5;
xp.normallyEvolve(shift);

%% Set desired charts and generate generate pullbacks
% KEEP GOING FROM THIS ONWARDS, EVERY SECTION
%
% Now we have the surface in a region of the data we would like to extract,
% and next we want to pullback the data to the various available charts. 
% By setting the desired charts option of the fitter, we specify which charts to 
% compute.
%
% Implemented charts are
% 
% * 'cylinder1_index', fundamental cylinder chart
% * 'cylinder2_index', fundamental cylinder chart rotated by 180 degrees
% * 'cylinder1_proper', modification of cylinder chart, measuring distance on the surface      
% * 'cylinder2_proper', modification of cylinder chart, measuring distance on the surface rotated by 180 degrees     
% * 'polarLowerZ', chart covering lower pole,          
% * 'polarUpperZ', chart covering upper pole,             
% * 'anteriorEquidistant', chart covering anterior pole measuring distance on the surface
% * 'posteriorEquidistant', chart covering posterior pole measuring distance on the surface 
%
xp.fitter.setDesiredChart('cylinder1_proper',1);
xp.fitter.setDesiredChart('cylinder2_proper',0);
xp.fitter.setDesiredChart('polarLowerZ',0);
xp.fitter.setDesiredChart('polarUpperZ',0);
xp.fitter.setDesiredChart('anteriorEquidistant',0);
xp.fitter.setDesiredChart('posteriorEquidistant',0);
xp.generateSOI();

%% Pullback the stack to the desired charts
%
% Pass the region of interest and the current time to pull back the stack
% in the desired charts. This generates the data fields containing the
% pullback.
%
onionOpts = struct('nLayers', 21, 'layerDistance', 1, 'sigma', 20,'makeIP', false);
xp.SOI.pullbackStack(xp.stack, xp.currentROI, xp.currentTime, onionOpts);

%%  visualize the pullback on cylinder1_proper 
%
% Now we extract the data field from the surface of interest at the current
% time, which is the time of the fit.
%
data = xp.SOI.getField('data');
data = data(xp.tIdx(xp.currentTime));
%%
%
% then we specify, which chart over which patch we would like to use to 
% inspect the pullback. The following combinations of patch and transformation 
% are currently possible:
%
% * 'cylinder1_index', 'cylinder1'
% * 'cylinder1_index', 'cylinder1_proper'
% * 'cylinder2_index', 'cylinder2'
% * 'cylinder2_index', 'cylinder2_proper'
% * 'polarLowerZ_index', 'polarLowerZ'
% * 'polarUpperZ_index', 'polarUpperZ'
% * 'posteriorEquidistant_index', 'posteriorEquidistant'
% * 'anteriorEquidistant_index', 'anteriorEquidistant'
% 
% Remember that the chart needs to be specified as a desired chart, if you
% want to inspect the pullback to it. 
%
% This is an example that inspects the cylinder1_proper transform over the
% cylinder1_index patch. 
%
patchName     = 'cylinder1_index';
transformName = 'cylinder1';
pb = data.getPatch(patchName).getTransform(transformName).apply{1};
figure, imshow(pb',[],'InitialMagnification',66)

%% Save the surface of interest to disc
%
% Here we save the SOI using SOI.save. We set the following options:
%
% * dir:            The directory to save the SOI to.
% * imwriteOptions: Pullbacks are saved to image files using imwrite, we
% can pass options to change file format, compression etc. For example we
% could change this option to
% imwriteOptions = {'jp2', 'Mode', 'lossless'}; 
% * make8bit:       Often absolute intensities don't matter and 8 bit offers
% a large enough dynamic range. This options rescales the lookup table and
% converts to 8 bit before saving.
%
imwriteOptions = {'tif'};
saveDir = fullfile(dataDir, 'layers');

options = struct('dir',saveDir,'imwriteOptions',{imwriteOptions},...
                    'make8bit',false);
xp.SOI.save(options) 



%% Where is the data? 
% 
% In the above specified saveDir, there is a fields folder, containg the 
% pullbacks in data, the metric and embedding for each desired chart as
% well as charts and transition maps in the atlas - each as a tif image for
% convenient inspection with other software such as Fiji. 

%% Load a SOI from disc
%
% All metadata is saved in SOI.xml. Pullbacks, geometry and any other data
% defined on the surface are saved to image files in subdirectories 
% reflecting the structure of patches and coordinates explained earlier in 
% this tutorial. We can reload a surface of interest with
% SOI.load(directory)
%

%% batch mode, embedding:
%%
for t = 2 :  length(fileMeta.timePoints)  % index into fileMeta.timePoints, actual time will be fileMeta.timePoints(t)
    ['doing timepoint: ',int2str(t)]
    
    % load the data
    xp.loadTime(fileMeta.timePoints(t));
    xp.rescaleStackToUnitAspect();

    %    xp.fitter.populateSOI(xp.SOI);

    xp.SOI.pullbackStack(xp.stack, xp.currentROI, xp.currentTime, onionOpts);
    xp.SOI.save(options)

end
