%% shortcuts... (run once)
Z=aux_coord{1,1};
Y=aux_coord{1,2};
X=aux_coord{1,3};

%% EITHER, set exporting coordinate window - MANUAL
% (must be in units of pixels, hence INTEGERs)
xInterval = [ 0,400 ];
yInterval = [ 0,400 ];
zInterval = [ 0,400 ];

%% OR, set exporting coordinate window - FIT ALL
xInterval = [ floor(min(X(:))), ceil(max(X(:))) ];
yInterval = [ floor(min(Y(:))), ceil(max(Y(:))) ];
zInterval = [ floor(min(Z(:))), ceil(max(Z(:))) ];


%% sweep the z-slices
% determine the output image size
xSize = xInterval(2) - xInterval(1) +1;
ySize = yInterval(2) - yInterval(1) +1;
slice = zeros(ySize,xSize);

% and create images
for z = zInterval(1):zInterval(2),
	% all points that belong to the respective z-slice
	% and that fit into x,y intervals
	fittingPoints = find((z-0.5)< Z & Z <= (z+0.5) ...
	                   & xInterval(1) <= X & X <= xInterval(2) ...
	                   & yInterval(1) <= Y & Y <= yInterval(2));

	% query the original pixel (rounded) coordinates
	for point = fittingPoints,
		slice(round(Y(point))-yInterval(1)+1, round(X(point))-xInterval(1)+1) = 1;
	end

	['saving slice z=',z]
	dlmwrite(['~/img__',z,'.txt'],slice,' ');
end
