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
chart = 'cylinder1';

%% experiment metadata
corResFactor = 0.38;    %in microns per pixel, resolution of the original images


%% JUST RUN/EXECUTE THE REST OF THE FILE
%
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
[s_file,s_path,s_filter]=uiputfile([chart,'.txt'],'Save the file with projection metadata');
if s_file == 0
	['WARN: User canceled dialog, should not proceed further!']
else
	dlmwrite([s_path,'/',s_file(1:end-4),'_area',s_file(end-3:end)],aux_detg,' ');
end

% save also the relative sizes, derived from the min size
minArea = min(aux_detg(:));
dlmwrite([s_path,'/',s_file(1:end-4),'_relativeArea',s_file(end-3:end)],aux_detg./minArea,' ');


%% get the metric matrix (i.e., trasformation to get proper lengths on pullbacks)
aux_g        = SOI.getField('embedding').getPatch(aux_domName);

%% get 3D coordinates matrices -- instantiate the metric to every pixel point
aux_coord    = aux_g.apply();

%% aux_coord are now three matrices (of single/float type) of the same size as is the
% pullbacked/unwrapped image and holds z,y,x, respectively, component of original 3D coordinate
% of every pixel, now save it (while preserving and not-scaling the real values)
dlmwrite([s_path,'/',s_file(1:end-4),'coords_Z',s_file(end-3:end)],corResFactor*aux_coord{1,1},' ');
dlmwrite([s_path,'/',s_file(1:end-4),'coords_Y',s_file(end-3:end)],corResFactor*aux_coord{1,2},' ');
dlmwrite([s_path,'/',s_file(1:end-4),'coords_X',s_file(end-3:end)],corResFactor*aux_coord{1,3},' ');
