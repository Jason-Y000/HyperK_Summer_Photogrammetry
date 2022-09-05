clear all

% Change current figure
% set(0,'currentfigure',<Figure variable>)

% Workaround: NaN entries are blank when converted from Matlab
% to Excel. This means that if the last row or first row of Matlab array is
% NaN it'll appear as a blank in Excel that won't be read back
% when the file is loaded. Specify the rows and columns to read over.
%
% Note that we should probably just save the corners as .csv
% files in the future

% ----------------------------------------------------------------------- %
% Initialize some variables

input_dir = "/Users/jasonyuan/Desktop/Triumf Lab/Calibration Photos/Underwater/Pool Calibration Photos - June 29";

data_save_dir = "/Users/jasonyuan/Desktop/Triumf Lab/Calibration Photos/Rayotek Water";
save_pth = "/Users/jasonyuan/Desktop/Triumf Lab/Calibration Photos/Rayotek Water";

read_input = "";
filter_input = "";
corner_dir = "";

use_HighDistortion = true;
use_PartialDetections = true;
EstimateAlignment = true;

squareSize = 25; % mm — I don't think this is too important
expectedBoard = [7 9];  % Size of the expected board pattern used
downsize_factor = linspace(2,12,11);

% ----------------------------------------------------------------------- %
% Get all images from target directory

if read_input == ""
    all_img_ds = imageDatastore(input_dir,'FileExtensions',[".jpg",".JPG"]);
%     all_img_extra = imageDatastore("/Volumes/UOFT NOTES/Rayotek_EZTops Calibration photos/Rayotek Calibration Photos",'FileExtensions',[".jpg",".JPG"]);

    files = all_img_ds.Files;
%     files = [files; all_img_extra.Files]; % Added for Rayotek Underwater
else
    files = readcell(read_input);

    if ~(filter_input == "")
        files = setxor(files,readcell(filter_input));
    end
end

% ----------------------------------------------------------------------- %
% Detect calibration pattern

imgPoints = double.empty(0,0,0);
imagesUsed = [];

if ~(read_input == "") && ~(corner_dir == "")

    num_corners = (expectedBoard(1)-1)*(expectedBoard(2)-1);

    for n = 1:size(files)
        [pth, name, extension] = fileparts(files{n,1});

        corner_name = [dir(corner_dir+"/"+name+"_*")];

        if isempty(corner_name)
            fprintf("Missing corner file for %s", name);
            imagesUsed = [imagesUsed; 0];
        else
            % Corner files save the information of Mx2 matrices, where M is
            % equal to the number of corners
            
            img_corner = readmatrix(corner_dir+"/"+corner_name.name, ...
                'Range',[1,1,num_corners,2]);
            
            imgPoints(:,:,end+1) = img_corner;
            imagesUsed = [imagesUsed; 1];
        end
    end
else
    for n = 1:size(files)
    
        I = imread(files{n,1});

        for i = downsize_factor
            [img_corners,boardSize] = map_corners(I,i,use_PartialDetections,use_HighDistortion,expectedBoard);
            if isequal(boardSize,expectedBoard) || isequal(boardSize,[expectedBoard(2),expectedBoard(1)])
                break
            end
        end

        if isequal(boardSize,expectedBoard) || isequal(boardSize,[expectedBoard(2),expectedBoard(1)])
            imgPoints(:,:,end+1) = img_corners;
            imagesUsed = [imagesUsed; 1];
        else
            imagesUsed = [imagesUsed; 0];
        end
    end
end

% For OpenCV corners
% imgPoints = load("/Users/jasonyuan/Desktop/Triumf Lab/Calibration Photos/Underwater_Corners_Rayotek/With OpenCV corner detection - July 6/all_corners.mat");
% imgPoints = double(imgPoints.corners);
% highest_errors = load("/Users/jasonyuan/Desktop/Triumf Lab/Calibration Photos/Underwater_Corners_Rayotek/With OpenCV corner detection - July 6/highest_errors.mat");
% highest_errors = highest_errors.highest_errors;
% imgToUse = double.empty(48,2,0);
% 
% for i = 1:size(imgPoints,3)
%     if sum(highest_errors' == i) == 1
%         continue
%     end
%     imgToUse(:,:,end+1) = imgPoints(:,:,i);
% end
% imgPoints = imgToUse;

% [imgPoints, boardSize, imagesUsed] = detectCheckerboardPoints(all_img_ds.Files,'HighDistortion',use_HighDistortion ...
%     ,'PartialDetections',use_PartialDetections);

% ----------------------------------------------------------------------- %
% Plot the detected corners to see what sort of distribution we have to
% work with
% Could also make a 2D histogram and have a count of the corners
% detected in certain patches

f1 = figure('Name','Corner distribution of calibration images');
f1.Visible = 'off';
for n = 1:size(imgPoints,3)
    plot(imgPoints(:,1,n),imgPoints(:,2,n),'LineStyle','none','Marker','.','MarkerEdgeColor','green','MarkerSize',15);
    hold on;
end
xlim([0 9504]);
ylim([0 6336]);
xlabel("x");
ylabel("y");
saveas(f1,save_pth+"/input_corner_distribution.jpg");

clf(f1, 'reset');

f1.Name = 'Distribution of detected corners by region';
f1.Visible = 'off';
xy_data = reshape(permute(imgPoints,[1,3,2]),[],2);
histogram2(xy_data(:,1),xy_data(:,2));
xlabel("x");
ylabel("y");
savefig(f1,save_pth+"/input_corner_histogram.fig");

% ----------------------------------------------------------------------- %
% Find world points

worldPoints = generateCheckerboardPoints(expectedBoard,squareSize);

% ----------------------------------------------------------------------- %
% Fisheye camera calibration

I = imread(files{1,1});

% For OpenCV corners
% I = imread("/Users/jasonyuan/Desktop/Triumf Lab/Calibration Photos/Underwater/Pool Calibration Photos - June 29/Pool_2.JPG");

imageSize = [size(I,1), size(I,2)];
[params, num_imgs, errors] = estimateFisheyeParameters(imgPoints,worldPoints,imageSize ...
    ,"EstimateAlignment",EstimateAlignment);

% ----------------------------------------------------------------------- %
% Plot and save reprojection error as well as scatterplot pixel coordinate
% reprojection error

img_reprojection_error = [];
e_vec = sqrt((params.ReprojectionErrors(:,1,:)).^2 + (params.ReprojectionErrors(:,2,:)).^2);

for i = 1:size(e_vec,3)
    sum = 0;
    N_count = 0;
    for j = 1:size(e_vec(:,:,i),1)
        if ~isnan(e_vec(j,:,i))
            sum = sum + e_vec(j,:,i);
            N_count = N_count + 1;
        end
    end
    sum = sum/N_count;
    img_reprojection_error(end+1,1) = sum;
end

f = figure('Name','Reprojection Error'); 
showReprojectionErrors(params);
saveas(f,save_pth+"/reprojection_error.jpg");

f2 = figure('Name','Reprojection Error of different image coordinates');
scatter3(reshape(imgPoints(:,1,:),[],1),reshape(imgPoints(:,2,:),[],1),reshape(e_vec,[],1),reshape(e_vec,[],1)*10,reshape(e_vec,[],1),'filled');
colorbar;
xlabel("x");
ylabel("y");
savefig(f2,save_pth+"/img_reprojection_error.fig");

% ----------------------------------------------------------------------- %
% Save the Fisheye Camera params and errors

save(save_pth+"/cameraParams.mat","params");
save(save_pth+"/cameraErrors.mat","errors");

% ----------------------------------------------------------------------- %
% Find the images that were not used in calibration, if any, and save them
% along with the images that exceed a certain reprojection error threshold

threshold = 2.00;

not_used_imgs = {};
used_imgs = {};
highest_errors = {};
for i = 1:length(imagesUsed)
    if imagesUsed(i,1) ~= 1
        not_used_imgs{length(not_used_imgs)+1,1} = files{i,1};
    else
        used_imgs{length(used_imgs)+1,1} = files{i,1};
    end
end
writecell(not_used_imgs,data_save_dir+"/Not_Used_Images.xlsx");
writecell(used_imgs,data_save_dir+"/Used_Images.xlsx");

for i=1:size(used_imgs,1)
    if img_reprojection_error(i,1) > threshold
        highest_errors{end+1,1} = used_imgs{i,1};
    end
end
writecell(highest_errors,data_save_dir+"/Highest_Reprojection_Errors.xlsx");

% ----------------------------------------------------------------------- %
% Save the corners of all the images that were used for calibration

if read_input == ""
    
    if ~isfolder(data_save_dir+"/Corners")
        mkdir(data_save_dir+"/Corners");
    end

    for n = 1:length(used_imgs)
    
        % Get the image's basename and create the save names
        split = strsplit(used_imgs{n,1},"/");
        filename = strsplit(split{1,length(split)},".");
        basename = filename{1,1};
    
        corners_save = basename + sprintf("_imgPoints_%d_%d.xlsx",boardSize(1,1),boardSize(1,2));
        
        writematrix(imgPoints(:,:,n), data_save_dir + "/Corners/" + corners_save);
    end
end
