# Camera Calibration

All the camera calibration code that was used in the summer is in this folder. Note that while the Python scripts and notebook are similar, there might be some differences between them and it is probably better to start with the notebooks before using the scripts


- Matlab camera calibration folder has all the MATLAB calibration scripts
  - cameraCalib.m: Main camera calibration script
  - map_corners.m: Downsize corner finding implementation in MATLAB
  - reprojectImage.m: Create a plot for an input chessboard image of its detected key points and the reprojected points and another plot
  showing the reprojection error at each detected key point location
  - Test_Stuff.m: Some testing code to convert the input data from excel corner files into a format usable for BabelCalib


- Python Camera Calibration folder holds the Python calibration scripts and notebooks
  - calibrateCamera.py: Main camera calibration script with some associated helper functions
  - downsize_corner_finder.py: Downsize corner finder implementation with OpenCV library
  - find_corner_errors.py: Exported version of Xiaoyue's corner finding error notebook
  - cameracalibration.ipynb: Notebook implementation of calibrateCamera.py. There may be some updates in the notebook not found in the script
  - Chessboard_Playground_Notebook.ipynb: A notebook for testing certain chessboard corner detection related codes
  - downsize_corner_notebook.ipynb: A notebook that implements parts of the downsize_corner_finder.py script
  - find_corner_errors.ipynb: Xiaoyue's corner finding error notebook
