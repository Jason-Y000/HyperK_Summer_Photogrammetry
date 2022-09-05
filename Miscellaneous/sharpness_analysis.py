import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def plot_sharpness_distance(pth,save_dir):

    """
    Given a CSV file with sharpness and distance data, plot them.
    CSV file should be formatted with headers: distance, average MTF50,
    weighted average MTF50 and orientation

    """

    df = pd.read_csv(pth)
    df.sort_values(by=['Orientation'],inplace=True)
    df.reindex()

    C_orient = []
    R_orient = []
    L_orient = []

    for row in df.itertuples(index=False):
        if (row.Orientation.lower() == 'c'):
            C_orient.append([row.Distance, row._1, row._2])
        elif (row.Orientation.lower() == 'r'):
            R_orient.append([row.Distance, row._1, row._2])
        elif (row.Orientation.lower() == 'l'):
            L_orient.append([row.Distance, row._1, row._2])


    C_orient = np.array(C_orient)
    R_orient = np.array(R_orient)
    L_orient = np.array(L_orient)

    fig = plt.figure()

    if (len(C_orient) != 0):
        ax1 = fig.add_subplot(2, 1, 1, label='Avg')
        ax2 = fig.add_subplot(2, 1, 2, label='Weighted Avg')

        ax1.plot(C_orient[:,0], C_orient[:,1], marker='x', color='b', markersize=5, linestyle='None', label='Avg')
        ax1.set_xlabel('Distance (cm)')
        ax1.set_ylabel('MTF50 (C/P)')
        ax1.set_title('Average MTF50 against distance')
        ax1.grid(linestyle='--', color='silver')
        ax1.legend(loc='best')

        ax2.plot(C_orient[:,0], C_orient[:,2], marker='o', color='r', markersize=5, linestyle='None', label='Weighted Avg')
        ax2.set_xlabel('Distance (cm)')
        ax2.set_ylabel('MTF50 (C/P)')
        ax2.set_title('Weighted Average MTF50 against distance')
        ax2.grid(linestyle='--', color='silver')
        ax2.legend(loc='best')

        fig.tight_layout()
        fig.savefig(save_dir+"/Center_Frame_Sharpness.png",bbox_inches='tight',format='png',dpi=600)
        fig.clf()

    if (len(R_orient) != 0):
        ax1 = fig.add_subplot(2, 1, 1, label='Avg')
        ax2 = fig.add_subplot(2, 1, 2, label='Weighted Avg')

        ax1.plot(R_orient[:,0], R_orient[:,1], marker='x', color='b', markersize=5, linestyle='None', label='Avg')
        ax1.set_xlabel('Distance (cm)')
        ax1.set_ylabel('MTF50 (C/P)')
        ax1.set_title('Average MTF50 against distance')
        ax1.grid(linestyle='--', color='silver')
        ax1.legend(loc='best')

        ax2.plot(R_orient[:,0], R_orient[:,2], marker='o', color='r', markersize=5, linestyle='None', label='Weighted Avg')
        ax2.set_xlabel('Distance (cm)')
        ax2.set_ylabel('MTF50 (C/P)')
        ax2.set_title('Weighted Average MTF50 against distance')
        ax2.grid(linestyle='--', color='silver')
        ax2.legend(loc='best')

        fig.tight_layout()
        fig.savefig(save_dir+"/Right_Frame_Sharpness.png",bbox_inches='tight',format='png',dpi=600)
        fig.clf()

    if (len(L_orient) != 0):
        ax1 = fig.add_subplot(2, 1, 1, label='Avg')
        ax2 = fig.add_subplot(2, 1, 2, label='Weighted Avg')

        ax1.plot(L_orient[:,0], L_orient[:,1], marker='x', color='b', markersize=5, linestyle='None', label='Avg')
        ax1.set_xlabel('Distance (cm)')
        ax1.set_ylabel('MTF50 (C/P)')
        ax1.set_title('Average MTF50 against distance')
        ax1.grid(linestyle='--', color='silver')
        ax1.legend(loc='best')

        ax2.plot(L_orient[:,0], L_orient[:,2], marker='o', color='r', markersize=5, linestyle='None', label='Weighted Avg')
        ax2.set_xlabel('Distance (cm)')
        ax2.set_ylabel('MTF50 (C/P)')
        ax2.set_title('Weighted Average MTF50 against distance')
        ax2.grid(linestyle='--', color='silver')
        ax2.legend(loc='best')

        fig.tight_layout()
        fig.savefig(save_dir+"/Left_Frame_Sharpness.png",bbox_inches='tight',format='png',dpi=600)
        fig.clf()

    return True

def main():

    data_path = "/Users/jasonyuan/Desktop/Triumf Lab/Image Quality Test Photos/Distance Quality Tests/No Dome/June 3/Sharpness_Distance.csv"
    save_dir = "/Users/jasonyuan/Desktop"

    plot_sharpness_distance(data_path,save_dir)

if __name__ == "__main__":
    main()
