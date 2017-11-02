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

%% experiment "27":
corResFactor = 0.38;    %in microns per pixel, resolution of the original images


%% reach the chart data
aux_chart    = SOI.atlas(timePoint).getChart(chart);
aux_stepSize = aux_chart.image.stepSize;
aux_domName  = aux_chart.domain.name;
%NB: aux_stepSize is not used

%% get the metric matrix (i.e., trasformation to get proper lengths on pullbacks)
aux_g        = SOI.getField('embedding').getPatch(aux_domName);

%% get 3D coordinates matrices -- instantiate the metric to every pixel point
aux_coord    = aux_g.apply();

%% aux_coord are now three matrices (of single/float type) of the same size as is the
% pullbacked/unwrapped image and holds z,y,x, respectively, component of original 3D coordinate
% of every pixel, now save it (while preserving and not-scaling the real values)
[s_file,s_path,s_filter]=uiputfile([chart,'.txt'],'Save the files with pixel coordinates');
dlmwrite([s_path,'/',s_file(1:end-4),'_Z',s_file(end-3:end)],corResFactor*aux_coord{1,1},' ');
dlmwrite([s_path,'/',s_file(1:end-4),'_Y',s_file(end-3:end)],corResFactor*aux_coord{1,2},' ');
dlmwrite([s_path,'/',s_file(1:end-4),'_X',s_file(end-3:end)],corResFactor*aux_coord{1,3},' ');
