function [f1, f2, mean_error] = reprojectImage(I, imagePoints, worldPoints, cameraIntrinsics, rotMat, tVec)

   reProjected_points = worldToImage(cameraIntrinsics, rotMat, tVec, worldPoints);
   
   % -------------------------------------------------------------------- %
   % Plot the reprojected image points and the image points onto the image

   f1 = figure ("Name","Reprojected Image Points and Original Image Points");
   imshow(I);
   hold on;
   
   plot(imagePoints(:,1), imagePoints(:,2),"LineStyle","none","Marker",".","MarkerEdgeColor","green","MarkerSize",10);
   label1 = "Image Points";
   hold on;
   
   plot(reProjected_points(:,1), reProjected_points(:,2),"LineStyle","none","Marker","x","MarkerEdgeColor","red","MarkerSize",8);
   label2 = "Reprojected Points";
   
   legend(label1, label2);
   title("Reprojected Image Points and Original Image Points");
   hold off;

   % -------------------------------------------------------------------- %
   % Create color map indicating pixel error intensities 

   pixel_error = [];
   mean_error = 0;

   for n = 1:size(imagePoints,1)
       px_error = sqrt((reProjected_points(n,1) - imagePoints(n,1))^2 + (reProjected_points(n,2) - imagePoints(n,2))^2);
       pixel_error = [pixel_error;px_error];
%        mean_error = mean_error + px_error^2; % Using RMSE
       mean_error = mean_error + px_error; % Using cumulative average
   end

%    mean_error = sqrt(mean_error/size(pixel_error,1)); % Using RMSE
   mean_error = mean_error/size(pixel_error,1); % Using cumulative average
   
   f2 = figure("Name","Reprojection error in image");
   I_annotated = insertObjectAnnotation(I,"circle",[imagePoints pixel_error*10],pixel_error',"FontSize",72,"TextColor","black");
   I_annotated = insertText(I_annotated,[size(I,2),size(I,1)],sprintf("Mean Error: %0.3f", mean_error),"AnchorPoint","RightBottom","FontSize",200);
   
   image(I_annotated);
   truesize(f2);
   hold on;
   scatter(imagePoints(:,1),imagePoints(:,2),pixel_error*25,pixel_error','filled','o');
   hold on;
   colorbar;

   title("Reprojection Error of each corner location");
   xlabel("x");
   ylabel("y");
   
   hold off;
    
end