"""
Detect corner coordinates by downsizing high resolution images to lower res
and then mapping the detected coordinates to the original image for further
enhancement

"""

import os
import matplotlib.pyplot as plt
import numpy as np
import cv2
import pandas as pd
import multiprocessing
import time
from scipy import io

nrows = 6   # Number of internal corner rows to be found
ncols = 8   # Number of internal corner cols to be found

criteria = (cv2.TERM_CRITERIA_EPS, 30, 0.00001)
flags = cv2.CALIB_CB_NORMALIZE_IMAGE + cv2.CALIB_CB_ACCURACY

def callCheckerboardCorners(I, size, flags, return_dict):
    ret, corners = cv2.findChessboardCornersSB(I, size, flags)
    return_dict["ret"] = ret
    return_dict["corners"] = corners

def get_downsized_corners(I):

    """
    Find the checkerboard corner coordinates in downsized image
    """

    I_rows, I_cols = I.shape[0], I.shape[1]
    aspect_ratio = I_cols/I_rows

    max_downsizing = 12

    downsize_factor = max_downsizing + 1

    for n in range(1,max_downsizing+1):

        manager = multiprocessing.Manager()
        return_dict = manager.dict()

        col_new = I_cols//n
        row_new = int(col_new/aspect_ratio)

        I_new = cv2.resize(I,(col_new,row_new),interpolation=cv2.INTER_AREA)
        I_new_gray = cv2.cvtColor(I_new, cv2.COLOR_BGR2GRAY)
        blurred_gray = cv2.bilateralFilter(I_new_gray, 3, 75, 75)
        # blurred_gray = cv2.GaussianBlur(gray, (35,35), 0)
        # blurred_gray = cv2.equalizeHist(blurred_gray.astype(np.uint8))

        # Start checkerboard corners as a process
        p = multiprocessing.Process(target=callCheckerboardCorners, args=(blurred_gray,(nrows,ncols),flags,return_dict))
        p.start()

        # Wait for the process to either finish or run for 10 s
        p.join(10)

        # If the thread is still alive and running, terminate
        if p.is_alive():
            print("Process killed for image size {} x {}".format(row_new,col_new))
            p.kill()
            p.join()
            continue
        else:
            p.join()
            # print(blurred_gray.shape)
            downsize_factor = n
            ret = return_dict["ret"]
            corners = return_dict["corners"]
            if not ret:
                continue
            break

    if (downsize_factor == max_downsizing + 1):
        return False, [], I, downsize_factor

    return ret, corners, blurred_gray, downsize_factor

def detect_corners_on_cropped_Chessboard(I,size,flags,row_min,row_max,col_min,col_max):

    """
    Try to find corners again on the cropped chessboard region
    """

    offset = 500 # 700 pixel offset
    x_min = max(col_min-offset,0)
    x_max = min(col_max+offset,I.shape[1])
    y_min = max(row_min-offset,0)
    y_max = min(row_max+offset,I.shape[0])

    cropped_region = I[y_min:y_max,x_min:x_max]

    cropped_gray = cv2.cvtColor(cropped_region, cv2.COLOR_BGR2GRAY)
    blurred_gray = cv2.bilateralFilter(cropped_gray, 3, 75, 75)

    ret, corners = cv2.findChessboardCornersSB(blurred_gray, size, flags)

    if ret:
        corners = cv2.cornerSubPix(blurred_gray, corners, (17,17), (-1,-1), criteria)
        corners[:,:,0] = corners[:,:,0] + x_min
        corners[:,:,1] = corners[:,:,1] + y_min

    return ret, corners

if __name__ == "__main__":

    # pth = "/Users/jasonyuan/Desktop/Triumf Lab/Calibration Photos/Underwater/Pool Calibration Photos - June 29/Pool_7.JPG"
    save_dir = "/Users/jasonyuan/Desktop/EZTops Corners Analysis Pool/OpenCV"
    dir = "/Users/jasonyuan/Desktop/EZTops Pool Calib"

    all_corners = []
    used_files = []
    not_used = []
    n = 0

    for file in os.listdir(dir):
        # print(n)
        # print(file)
        if file == ".DS_Store":
            continue

        img = cv2.imread(dir+"/"+file)
        # gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        # blurred_gray = cv2.bilateralFilter(gray,3,75,75)
        # blurred_gray = cv2.equalizeHist(blurred_gray.astype(np.uint8))
        # ret,corners = cv2.findChessboardCorners(blurred_gray, (nrows,ncols), None)
        ret,corners,im_gray,downsize_factor = get_downsized_corners(img)

        if ret:
            print("{} has detected corners with downsize factor {}".format(file,downsize_factor))

        if (ret) and (downsize_factor == 1):
            used_files.append(file)
            corners2 = cv2.cornerSubPix(im_gray, corners, (17,17), (-1,-1), criteria)
            all_corners.append(np.squeeze(corners2))

        elif (ret) and (downsize_factor > 1):
            col_min = np.intc(np.min(corners[:,:,0])*downsize_factor)
            col_max = np.intc(np.max(corners[:,:,0])*downsize_factor)
            row_min = np.intc(np.min(corners[:,:,1])*downsize_factor)
            row_max = np.intc(np.max(corners[:,:,1])*downsize_factor)

            ret2, corners2 = detect_corners_on_cropped_Chessboard(img,(nrows,ncols),flags,row_min,row_max,col_min,col_max)

            if ret2:
                used_files.append(file)
                all_corners.append(np.squeeze(corners2))
            else:
                corners2 = cv2.cornerSubPix(cv2.cvtColor(img,cv2.COLOR_BGR2GRAY),corners*downsize_factor,(17,17),(-1,-1),criteria)
                used_files.append(file)
                all_corners.append(np.squeeze(corners2))
                
                # not_used = not_used + [file]

        else:
            not_used = not_used + [file]

        n += 1

    df = pd.DataFrame({"used_files": used_files, "corners": all_corners})
    df.to_csv(save_dir+"/used_files.csv")

    np.savetxt(save_dir+"/all_corners_{}.csv".format(np.array(all_corners).shape), np.array(all_corners).flatten(), delimiter=",")
    io.savemat(save_dir+"/all_corners.mat", {"corners": np.array(all_corners).transpose(1,2,0)})

    # img = cv2.imread(pth)
    # im_copy = np.copy(img)
    # ret, corners, im_gray, downsize_factor = get_downsized_corners(img)
    #
    # # print(ret)
    # # print(corners.shape)
    # # print(corners)
    # # print(downsize_factor)
    #
    # # I_new_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # # blurred_gray = cv2.bilateralFilter(I_new_gray, 3, 75, 75)
    # # # blurred_gray = cv.GaussianBlur(gray, (35,35), 0)
    # # blurred_gray = cv2.equalizeHist(blurred_gray.astype(np.uint8))
    # #
    # # ret, corners = cv2.findChessboardCorners(blurred_gray, (nrows,ncols), None)
    # #
    # # print(ret)
    #
    # if downsize_factor > 1:
    #     col_min = np.intc(np.min(corners[:,:,0])*downsize_factor)
    #     col_max = np.intc(np.max(corners[:,:,0])*downsize_factor)
    #     row_min = np.intc(np.min(corners[:,:,1])*downsize_factor)
    #     row_max = np.intc(np.max(corners[:,:,1])*downsize_factor)
    #
    #     ret2, corners2 = detect_corners_on_cropped_Chessboard(img,(nrows,ncols),flags,row_min,row_max,col_min,col_max)
    #     # print(ret2)
    #
    # drawn = cv2.drawChessboardCorners(cv2.resize(im_copy,(im_copy.shape[1]//downsize_factor,im_copy.shape[0]//downsize_factor)), (nrows,ncols), corners, ret)
    # # print(drawn.shape)
    #
    # if downsize_factor > 1:
    #     drawn2 = cv2.drawChessboardCorners(np.copy(img),(nrows,ncols),corners2,ret2)
    #     cv2.imshow("Original Size Detection",drawn2)
    #
    #     offset = 700 # 700 pixel offset
    #     x_min = max(col_min-offset,0)
    #     x_max = min(col_max+offset,img.shape[1])
    #     y_min = max(row_min-offset,0)
    #     y_max = min(row_max+offset,img.shape[0])
    #
    #     cropped_region = drawn2[y_min:y_max,x_min:x_max]
    #
    #     cv2.imshow("Cropped Region", cropped_region)
    #
    # cv2.imshow("Corners",drawn)
    # cv2.imshow("Original",img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
