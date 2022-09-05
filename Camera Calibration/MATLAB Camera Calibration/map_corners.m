function [avg_corners,boardSize] = map_corners(I,downsize_factor,usePartialDetections,useHighDistortion,expectedBoardSize)
    
    function d = euclideanDistance(x,y)
        d = sqrt(x^2+y^2);
    end
    
    % Return statements for debugging purposes
    %[avg_corners,boardSize] - †his is the desired output
    %[img_corners,boardSize]
    %[imgP_down, boardSize_down]
    %[x_min,x_max,y_min,y_max]

    % Using a downsized image, find the location of the checkerboard and
    % then map the approximate location to the original image for
    % checkerboard corners detection
    
    % Offset factor to capture the edges of the board in pixels
    offset_factor = 500;    % Change to 500 if using smaller board

    I_resized = imresize(I,1/downsize_factor,"bilinear");
    
    [imgP_down, boardSize_down] = detectCheckerboardPoints(I_resized,'PartialDetections',usePartialDetections,'HighDistortion',useHighDistortion);
    
    x_max = -inf;
    x_min = inf;
    y_max = -inf;
    y_min = inf;

    for n=1:size(imgP_down,1)
        
        if imgP_down(n,1) < x_min
            x_min = imgP_down(n,1);
        end
        if imgP_down(n,1) > x_max
            x_max = imgP_down(n,1);
        end
        if imgP_down(n,2) < y_min
            y_min = imgP_down(n,2);
        end
        if imgP_down(n,2) > y_max
            y_max = imgP_down(n,2);
        end
    end

    % Crop out expected checkerboard region and run the detectcheckerboard
    % corners once again
    
    x_min = max([round(x_min*downsize_factor)-offset_factor 1]);
    x_max = min([round(x_max*downsize_factor)+offset_factor size(I,2)]);
    y_min = max([round(y_min*downsize_factor)-offset_factor 1]);
    y_max = min([round(y_max*downsize_factor)+offset_factor size(I,1)]);
    
    if isequal(boardSize_down,[0 0])
        avg_corners = [];
        boardSize = [0 0];
        return;
    end

    [img_corners, boardSize] = detectCheckerboardPoints(I(y_min:y_max,x_min:x_max,:),'PartialDetections',usePartialDetections,'HighDistortion',useHighDistortion);
    
    if ~isempty(img_corners)
        img_corners(:,1) = img_corners(:,1) + x_min;
        img_corners(:,2) = img_corners(:,2) + y_min;
    end
    
    if ~isequal(boardSize,expectedBoardSize) && ~isequal(boardSize,[expectedBoardSize(2) expectedBoardSize(1)])
        
        if isequal(boardSize_down,expectedBoardSize) || isequal(boardSize_down,[expectedBoardSize(2) expectedBoardSize(1)])
            avg_corners = imgP_down.*downsize_factor;
            boardSize = boardSize_down;
            return;
        end

        avg_corners = [];
        boardSize = [0 0];
        return;
    else
        avg_corners = img_corners;
        return;
    end
    
    % ---- Below is the previous averaging approach. Above just -------- %
    % ---- attempts a redetection on the cropped checkeboard region ---- %

    % Average the detection of the up projected small image and the large
    % checkerboard detection
    % Use a Euclidean distance metric to average points detected in the
    % original and downscaled image. The error will approximately scale
    % proportional to the downsizing factor

    if (size(img_corners,1) == size(imgP_down,1)) && (isequal(boardSize,expectedBoardSize)) && (isequal(boardSize_down,expectedBoardSize))

        % Check which of the downsized or original corners has less NaN and
        % use as the base orientation
        
        num_NaN_down = sum(isnan(imgP_down));
        num_NaN_reg = sum(isnan(img_corners));

        if num_NaN_reg(:,1) > num_NaN_down(:,1)
            avg_corners = imgP_down*downsize_factor;
            
            for n = 1:size(avg_corners,1) 
                if (isnan(avg_corners(n,1)) || isnan(avg_corners(n,2)))
                    continue
                end
                x = avg_corners(n,1);
                y = avg_corners(n,2);

                for j = 1:size(img_corners,1)
                    if (isnan(img_corners(j,1)) || isnan(img_corners(j,2)))
                        continue
                    end
                    
                    x_p = img_corners(j,1);
                    y_p = img_corners(j,2);

                    if euclideanDistance(x-x_p,y-y_p) < 5
                        avg_corners(n,1) = (x+x_p)/2;
                        avg_corners(n,2) = (y+y_p)/2;
                    end
                end
            end
        else         
            avg_corners = img_corners;

            for n = 1:size(avg_corners,1) 
                if (isnan(avg_corners(n,1)) || isnan(avg_corners(n,2)))
                    continue
                end
                x = avg_corners(n,1);
                y = avg_corners(n,2);

                for j = 1:size(imgP_down,1)
                    if (isnan(imgP_down(j,1)) || isnan(imgP_down(j,2)))
                        continue
                    end
                    
                    x_p = imgP_down(j,1)*downsize_factor;
                    y_p = imgP_down(j,2)*downsize_factor;

                    if euclideanDistance(x-x_p,y-y_p) < 5
                        avg_corners(n,1) = (x+x_p)/2;
                        avg_corners(n,2) = (y+y_p)/2;
                    end
                end
            end
        end
    else
        if isequal(boardSize_down,expectedBoardSize)
            avg_corners = imgP_down*downsize_factor;
            boardSize = boardSize_down;
        elseif isequal(boardSize,expectedBoardSize)
            avg_corners = img_corners;
        else
            avg_corners = [];
            boardSize = [0 0];
        end
    end
end 