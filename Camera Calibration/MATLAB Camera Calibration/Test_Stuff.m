% Some stuff 

for n = 1:size(imgPoints,3)
train.corners(n).x = [];
train.corners(n).cspond = [];
for i = 1:size(imgPoints,1)
if ~isnan(imgPoints(i,1,n)) && ~isnan(imgPoints(i,2,n))
train.corners(n).x = [train.corners(n).x [imgPoints(i,1,n);imgPoints(i,2,n)]];
train.corners(n).cspond = [train.corners(n).cspond [i;1]];
end
end
end

worldPoints = generateCheckerboardPoints(expectedBoard,25);
boards = [];
boards.Rt = [eye(3) zeros(3,1)];
boards.X = worldPoints';