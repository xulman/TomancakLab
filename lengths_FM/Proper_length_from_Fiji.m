%
% author: Vladimir Ulman, ulman@mpi-cbg.de, 2017
%
% This function calculates the proper lengths on projected images,
% this function requires access to the SOI.xml and to the *__ROIcoords.txt files.
%
% The function assumes that the proper SOI.xml is found in the current working
% directory. You need to adjust a couple of variables inside this function.
function Proper_length_from_Fiji()
	%% We start by clearing the memory and closing all figures.
	%
	% (run once at the beginning)
	clear all; close all;

	%% PLEASE, CHANGE WORKING DIRECTORY NOW to where the SOI file is
	%
	% This loads the experiment data (incl. transformation)
	%
	% (run once at the beginning)
	SOI = surfaceAnalysis.SurfaceOfInterest('.');

	%% PLEASE, ADJUST THE VARIABLES HERE
	%
	timePoint = 1;
	chart = 'cylinder1';
	pathToRoiFiles = uigetdir('','Where are your exported *ROI_coords.txt files?');
	% the path and files therein should match the SOI file!
	% NB: https://de.mathworks.com/help/matlab/ref/inputdlg.html

	%% experiment "16":
	corResFactor = 0.38;    %in microns per pixel, resolution of the original images
	corCoordsScaling = 1.0; %factor to multiply ROI coordinates before proper length is calculated
	timeDelayBetween = 1.5; %in minutes between consecutive frames

	%% experiment "27":
	corResFactor = 0.38;    %in microns per pixel, resolution of the original images
	corCoordsScaling = 2.0; %factor to multiply ROI coordinates before proper length is calculated
	timeDelayBetween = 2.0; %in minutes between consecutive frames


	%% this one processes a list of curves
	%
	% this one scans the folder 'pathToRoiFiles' for all "curve files"
	% (and stores it in a list 'curveFiles')
	curveFiles = dir([pathToRoiFiles,'/*__ROIcoords.txt']);

	% this prepares another lists ('curveTimes' and 'curveLengths')
	% with proper timepoints extracted from file names and proper lengths
	% calculated via ImSAnE
	curveTimes = zeros(size(curveFiles,1),1);
	curveLengths = zeros(size(curveFiles,1),1);
	for i=1:size(curveFiles,1)
		% current file to be processed
		name = curveFiles(i).name;

		% reads the file and extracts the proper timepoint
		curve = dlmread([pathToRoiFiles,'/',name]);
		idxs = find(name == '_');
		time = str2num( name(idxs(end-2)+1:idxs(end-1)-1) );

		% extracts the proper length and stores both pieces of infomation
		curveLengths(i) = corResFactor * ...
		        SOI.properLength(timePoint, corCoordsScaling.*curve, chart);

		% this may fail whenever curve starts/ends close to the image border
		% check if it had failed and iteratively repeat on shorter curve then
		shortening=0;
		while and( not(curveLengths(i) > 0), shortening < 20 ),
			curve=curve(2:end-1,:);
			curveLengths(i) = corResFactor * ...
			        SOI.properLength(timePoint, corCoordsScaling.*curve, chart);
			shortening = shortening+1;
		end
		if shortening > 0
			['WARN: Needed ',num2str(shortening),' to obtain meaningful length for time point ',num2str(time)]
		end
		curveTimes(i) = time;
	end

	% convert z-slices to the actual times
	curveTimes = curveTimes * timeDelayBetween;
    
    % warn user to check for WARN messages
    ['Please, scroll up to see if there are any WARN messages.']

	%%
	% remove empty time points (but there should NOT be any now)
	curveLengths = curveLengths(curveTimes>0);
	curveTimes = curveTimes(curveTimes>0);

	%%
	% sort arrays according to the times
	[curveTimes,sortPermutation] = sort(curveTimes);
	curveLengths = curveLengths(sortPermutation);

	%%
	% display the plot with the proper timepoints and proper lengths
	plot(curveTimes,curveLengths,'-');
	title('Curve length over time');
	xlabel('time (minutes)');
	ylabel('length (micrometers)');

	%%
	% export the values used to create the plot
	ee = eye(2);
	exp = curveTimes*ee(1,:) + curveLengths*ee(2,:);
	dlmwrite([pathToRoiFiles,'/properTimesAndLengths.dat'],exp,' ');
	dlmwrite([pathToRoiFiles,'/properLengthsAlone.dat'],curveLengths,' ');
end



%% OBSOLETE, per one file processing:
%
% loads the curve file that was exorted from Fiji
%curve = dlmread('~/Desktop/projection_5.tif__ROIcoords.txt');
% cacl the proper PIXEL length along the curve
%SOI.properLength(1,curve,'cylinder1')
