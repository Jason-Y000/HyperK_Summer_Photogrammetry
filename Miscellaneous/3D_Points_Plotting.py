import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def ascii_parser(f_pth):

    df = pd.read_csv(f_pth,sep=',',header=None,names=['Points','x','y','z'])
    all_values = df.to_numpy()

    points = all_values[:,0].tolist()
    x_coords = all_values[:,1].tolist()
    y_coords = all_values[:,2].tolist()
    z_coords = all_values[:,3].tolist()

    return points,x_coords,y_coords,z_coords

def plot_3d_points(figure,colour,label,points,x_coords,y_coords,z_coords):

    x = np.array(x_coords)
    y = np.array(y_coords)
    z = np.array(z_coords)

    ax = figure.gca(projection='3d')
    ax.scatter(x,y,z,s=15,c=colour,label=label)
    for lbl, x_val, y_val, z_val in zip(points,x,y,z):
        ax.text(x_val,y_val,z_val,lbl,size=10)

    return figure

if __name__ == "__main__":

    data_dir = ""
    save_pth = ""
    figure = plt.figure()

    # Iterate through folder with all ASCII block files
    if os.path.isdir(data_dir):
        for i,file in enumerate(os.listdir(data_dir),0):
            if file == ".DS_Store" or not os.path.isfile(file):
                continue

            points,x,y,z = ascii_parser(data_dir+"/"+file)
            label = file.split(".")[0]
            figure = plot_3d_points(figure,np.random.rand(3),label,points,x,y,z)

    ax = figure.gca(projection='3d')

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_title("EZTops Dome 3D Scan points")
    ax.legend()

    figure.tight_layout()
    
    plt.savefig(save_pth+"/plot_of_points.png",bbox_inches='tight',format='png',dpi=600)
    plt.show()
