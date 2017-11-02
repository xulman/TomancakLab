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
% Will cause the computer to re-calculate the induced metric.
SOI.NCalcInducedMetric();


%% PLEASE, ADJUST THE VARIABLES HERE
%
%% this part creates an image that reports area of every pixel
timePoint = 1;
chart = 'cylinder2';

%% experiment "16":
corResFactor = 0.38;    %in microns per pixel, resolution of the original images
corCoordsScaling = 1.0; %factor to multiply ROI coordinates before proper length is calculated
timeDelayBetween = 1.5; %in minutes between consecutive frames

%% experiment "27":
corResFactor = 0.38;    %in microns per pixel, resolution of the original images
corCoordsScaling = 2.0; %factor to multiply ROI coordinates before proper length is calculated
timeDelayBetween = 2.0; %in minutes between consecutive frames


%% reach the chart data
aux_chart    = SOI.atlas(timePoint).getChart(chart);
aux_stepSize = aux_chart.image.stepSize;
aux_domName  = aux_chart.domain.name;

%% get the metric matrix (i.e., trasformation to get proper lengths on pullbacks)
aux_g        = SOI.g.getPatch(aux_domName).getTransform(chart);

%% get metric matrices -- instantiate the metric to every pixel point
aux_metric   = aux_g.apply();

%% for every pixel: get determinant of its metric, replace "broken" matrices
% with zeros, take sq. roots and correct for proper resolution
aux_detg = aux_metric{1,1}.*aux_metric{2,2}...
         - aux_metric{1,2}.*aux_metric{2,1};
aux_detg(isnan(aux_detg)) = 0;
% ImSAnE-side correction for resolution
aux_detg = sqrt(aux_detg)*aux_stepSize(1)*aux_stepSize(2);
% our-side correction for resolution
aux_res  = corResFactor * corResFactor;
aux_detg = aux_detg .* aux_res;

%% aux_detg is now a matrix (of single/float type) of the same size as is the
% pullbacked/unwrapped image and holds area of every pixel, now save it
% (while preserving and not-scaling the real values)
[s_file,s_path,s_filter]=uiputfile([chart,'.txt'],'Save the file with pixel areas');
dlmwrite([s_path,'/',s_file],aux_detg,' ');

% save also the relative sizes, derived from the min size
minArea = min(aux_detg(:));
dlmwrite([s_path,'/',s_file(1:end-4),'_relative',s_file(end-3:end)],aux_detg./minArea,' ');
