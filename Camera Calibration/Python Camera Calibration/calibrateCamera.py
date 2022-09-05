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

# Shape of the image
rows = 6336
cols = 9054

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
pinhole_flags = cv2.CALIB_USE_INTRINSIC_GUESS + cv2.CALIB_RATIONAL_MODEL
fisheye_flags = cv2.fisheye.CALIB_USE_INTRINSIC_GUESS + cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC

square_size = 25 # mm
deformation_vertex = 2.5 # mm

corner_pth = "/Users/jasonyuan/Desktop/Triumf Lab/Calibration Photos/Underwater_Corners_Rayotek/With OpenCV corner detection - July 6/all_corners_(247, 48, 2).csv"
K_pth = "/Users/jasonyuan/Desktop/Triumf Lab/Calibration Photos/Underwater_Corners_Rayotek/OpenCV calibration - July 8/Fisheye/Offset - -0.5mm/camIntrinsics_K_(3, 3).csv"
Knew_pth = "/Users/jasonyuan/Desktop/Triumf Lab/Calibration Photos/Underwater_Corners_Rayotek/OpenCV calibration - July 8/Fisheye/Offset - -0.5mm/camIntrinsics_Knew_(3, 3).csv"
dist_pth = "/Users/jasonyuan/Desktop/Triumf Lab/Calibration Photos/Underwater_Corners_Rayotek/OpenCV calibration - July 8/Fisheye/Offset - -0.5mm/distortion.csv"
rvecs_pth = "/Users/jasonyuan/Desktop/Triumf Lab/Calibration Photos/Underwater_Corners_Rayotek/OpenCV calibration - July 8/Fisheye/Offset - -0.5mm/rvecs_(247, 3, 1).csv"
tvecs_pth = "/Users/jasonyuan/Desktop/Triumf Lab/Calibration Photos/Underwater_Corners_Rayotek/OpenCV calibration - July 8/Fisheye/Offset - -0.5mm/tvecs_(247, 3, 1).csv"
save_pth = "/Users/jasonyuan/Desktop"

# fx = 3168
# fy = 3168
# cx = 4752.5
# cy = 3168.5

def initCameraIntrinsics(fx,fy,cx,cy):

    K = np.zeros((3,3),np.float32)
    K[0,0] = fx
    K[1,1] = fy
    K[2,2] = 1
    K[0,2] = cx
    K[1,2] = cy

    return K

def find_reprojection_error(objPoints, imgPoints, K, dist, rvecs, tvecs,cameraModel):

    num_images = objPoints.shape[0]
    e_points = []
    overall_mean_error = 0

    for n in range(num_images):

        if cameraModel == 0:
            reprojected_points,_ = cv2.projectPoints(np.array([objPoints[n,:,:]]), rvecs[n,:,:], tvecs[n,:,:], K, dist)
        else:
            reprojected_points,_ = cv2.fisheye.projectPoints(np.array([objPoints[n,:,:]]), rvecs[n,:,:], tvecs[n,:,:], K, dist)

        # Squeeze the imgPoints and reprojected_points to be Nx2
        error = np.squeeze(reprojected_points) - np.squeeze(imgPoints[n,:,:])
        e_vec = np.sqrt(np.power(error[:,0],2) + np.power(error[:,1],2)).reshape(-1,1)
        e_points.append(e_vec)

        overall_mean_error = overall_mean_error + np.mean(e_vec)

    e_points = np.array(e_points)   # Shape should be num_images x N x 1

    overall_mean_error = overall_mean_error/num_images

    return overall_mean_error, e_points

def get_UndistortedImage(distorted, K, dist, cameraModel, Knew=None, new_size=None):

    if new_size == None:
        new_size = (distorted.shape[1],distorted.shape[0])
    # map1,map2 = cv2.fisheye.initUndistortRectifyMap(K,dist,np.eye(3),new_K,(cols,rows),cv2.CV_16SC2)
    # undistorted = cv2.remap(distorted,map1,map2,cv2.INTER_LINEAR)

    if cameraModel == 0:
        undistorted = cv2.undistort(distorted, K, dist, newCameraMatrix=Knew)
    else:
        if Knew == None:
            Knew = K

        undistorted = cv2.fisheye.undistortImage(distorted,K,dist,Knew=Knew,new_size=new_size)

    return undistorted

def generate_objectPoints(nrows,ncols,deformation_vertex,square_size,img_shape):

    """
    nrows: Number of internal corner rows
    ncols: Number of interal corner columns
    deformation_vertex: Point of largest deviation
    square_size: Size of a chessboard square
    img_shape: Shape of the detected image points
    """

    # Object points are created like (0,0,0), (1,0,0), (2,0,0), ...
    objPoints = np.zeros((nrows*ncols,3),np.float32)
    objPoints[:,:2] = np.mgrid[0:nrows,0:ncols].T.reshape(-1,2)

    # Non-planar deformation to be characterized as a parabola
    # Assume that the square size is 25 mm and deformation is about 2.5 mm at
    # the location of its largest bump

    # f(y) = a(y-(ncols-1)/2)^2 + max_deformation
    a = -(deformation_vertex/square_size)/((ncols-1)/2)**2
    z_vals = a*np.power((np.array(range(ncols)) - (ncols-1)/2),2) + deformation_vertex/square_size

    objPoints[:,2] = np.repeat(z_vals,nrows)
    objectPoints = np.empty((img_shape[0],img_shape[1],3))
    objectPoints = np.tile(np.array([objPoints]),(img_shape[0],1,1))

    return objectPoints

def get_cameraParams(cameraModel,save_pth):

    # Read the corners from the saved CSV file
    df = pd.read_csv(corner_pth,header=None)
    imgPoints = df[0].to_numpy()

    imgPoints = imgPoints.reshape(-1,nrows*ncols,2)

    # ----------------------------------------------------------------------------- #
    # Read the file with the initial camera parameters if available

    if K_pth:
        df_K = pd.read_csv(K_pth,header=None)
        K = df_K[0].to_numpy()
        K = K.reshape((3,3))

    # if Knew_pth:
    #     df_Knew = pd.read_csv(Knew_pth,header=None)
    #     Knew = df_Knew[0].to_numpy()
    #     Knew = Knew.reshape((3,3))
    #
    # if dist_pth:
    #     df_dist = pd.read_csv(dist_pth,header=None)
    #     dist = df_dist[0].to_numpy()
    #
    # if rvecs_pth:
    #     df_rvecs = pd.read_csv(rvecs_pth,header=None)
    #     rvecs = df_rvecs[0].to_numpy()
    #     rvecs = rvecs.reshape((-1,3,1))
    #
    # if tvecs_pth:
    #     df_tvecs = pd.read_csv(tvecs_pth,header=None)
    #     tvecs = df_tvecs[0].to_numpy()
    #     tvecs = tvecs.reshape((-1,3,1))

    # K = initCameraIntrinsics(fx,fy,cx,cy)

    # ----------------------------------------------------------------------------- #

    # Create the non-planar world points

    objectPoints = generate_objectPoints(nrows,ncols,deformation_vertex,square_size,imgPoints.shape)

    # ----------------------------------------------------------------------------- #
    if cameraModel == 0:
        # Pinhole calibration
        ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(objectPoints.astype(np.float32), imgPoints.astype(np.float32), (cols,rows), K, np.zeros((1,6)), flags=pinhole_flags)
        new_K, roi = cv2.getOptimalNewCameraMatrix(K, dist, (cols,rows), 1, (cols,rows))

    else:
        # Fisheye calibration
        objectPoints = np.expand_dims(np.asarray(objectPoints), -2)
        imgPoints = np.expand_dims(np.asarray(imgPoints), -2)
        ret, K, dist, rvecs, tvecs = cv2.fisheye.calibrate(objectPoints.astype(np.float64), imgPoints.astype(np.float64), (cols,rows), K, np.zeros((1,4),dtype=np.float64), flags=fisheye_flags)
        new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(K,dist,(cols,rows),np.eye(3),balance=0,new_size=(cols,rows))

    # ----------------------------------------------------------------------------- #

    np.savetxt(save_pth+"/camIntrinsics_K_{}.csv".format(K.shape), K.flatten(),delimiter=",")
    np.savetxt(save_pth+"/camIntrinsics_Knew_{}.csv".format(new_K.shape), new_K.flatten(), delimiter=",")
    np.savetxt(save_pth+"/distortion.csv", dist.flatten(), delimiter=",")
    np.savetxt(save_pth+"/rvecs_{}.csv".format(np.array(rvecs).shape), np.array(rvecs).flatten(),delimiter=",")
    np.savetxt(save_pth+"/tvecs_{}.csv".format(np.array(tvecs).shape), np.array(tvecs).flatten(),delimiter=",")

    return True

def get_Reprojection_error(cameraModel):

    if K_pth:
        df_K = pd.read_csv(K_pth,header=None)
        K = df_K[0].to_numpy()
        K = K.reshape((3,3))

    if Knew_pth:
        df_Knew = pd.read_csv(Knew_pth,header=None)
        Knew = df_Knew[0].to_numpy()
        Knew = Knew.reshape((3,3))

    if dist_pth:
        df_dist = pd.read_csv(dist_pth,header=None)
        dist = df_dist[0].to_numpy()

    if rvecs_pth:
        df_rvecs = pd.read_csv(rvecs_pth,header=None)
        rvecs = df_rvecs[0].to_numpy()
        rvecs = rvecs.reshape((-1,3,1)).astype(np.float64)

    if tvecs_pth:
        df_tvecs = pd.read_csv(tvecs_pth,header=None)
        tvecs = df_tvecs[0].to_numpy()
        tvecs = tvecs.reshape((-1,3,1)).astype(np.float64)

    df = pd.read_csv(corner_pth,header=None)
    imgPoints = df[0].to_numpy()
    imgPoints = imgPoints.reshape(-1,nrows*ncols,2)

    objectPoints = generate_objectPoints(nrows,ncols,deformation_vertex,square_size,imgPoints.shape)

    mean_error, error_points = find_reprojection_error(objPoints, imgPoints, K, dist, rvecs, tvecs, cameraModel)

    return mean_error, error_points

def main():

    cameraModel = 1

    # Find the camera parameters for the chosen model
    get_cameraParams(cameraModel,save_pth)

    # Find the reprojection error for a given set of camera parameters
    mean_error, error_points = get_Reprojection_error(cameraModel)
    np.savetxt(save_pth+"/mean_error_{}_coord_reprojection_errors_{}.csv".format(mean_error,error_points.shape), error_points.flatten())

    return True

if __name__ == "__main__":
    main()
