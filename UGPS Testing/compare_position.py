"""
Compare the positional accuracy from GPS reading with hard set values

"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import json

def get_FIFISH_v6_metadata(metafile_pth):

    """
    Read FIFISH metadata and extract relevant contents into dictionary

    Relevant categories:
    - Timestamp
    - Depth
    - Euler
    - Water Quality
    - GPS
    - Sonar

    No water quality sensor so this type shouldn't be exported in the ROV log and
    current data extraction below does not account for the water quality entries

    Note that the occurrences column is for debugging purposes. Each timestamp
    should not have more than the number of non NaN data entries in its row

    Returns: pd.DataFrame of the parsed JSON frame. Each row is a complete entry
    of all available payload data for one timestamp

    """
    metadata_cvt = {}
    data_type_occurrences = {} # For debugging purposes
    time = []
    depth = []
    heading = []
    yaw = []
    pitch = []
    roll = []

    # Read in the JSON text data
    f = open(metafile_pth)
    json_data = json.load(f)
    f.close()

    for i in range(len(json_data)):
        timestamp = json_data[i]['timestamp']
        data_type = json_data[i]['type']
        payload = json_data[i]['payload']

        if timestamp not in metadata_cvt:
    # List saving entries: [depth, temperature, longitude, latitude, altitude, distance, left, right, roll, yaw, pitch, photo_type, timestamp]
            metadata_cvt[timestamp] = [np.nan]*13
            metadata_cvt[timestamp][12] = timestamp

            # For debugging
    # Save the number of times a 'type' of data occurs for a given timestamp
    # List entries as follows: [depth, sonar, gps, attitude, photo, timestamp]
            data_type_occurrences[timestamp] = [0]*6
            data_type_occurrences[timestamp][5] = timestamp

        if data_type == 'depth':
            metadata_cvt[timestamp][0] = payload['depth']
            metadata_cvt[timestamp][1] = payload['temperature']
            data_type_occurrences[timestamp][0] += 1

        if data_type == 'sonar':
            metadata_cvt[timestamp][4] = payload['altitude']
            metadata_cvt[timestamp][5] = payload['distance']
            metadata_cvt[timestamp][6] = payload['left']
            metadata_cvt[timestamp][7] = payload['right']
            data_type_occurrences[timestamp][1] += 1

        if data_type == 'gps':
            metadata_cvt[timestamp][2] = payload['longitude']
            metadata_cvt[timestamp][3] = payload['latitude']
            data_type_occurrences[timestamp][2] += 1

        if data_type == 'attitude':
            metadata_cvt[timestamp][8] = payload['roll']
            metadata_cvt[timestamp][9] = payload['yaw']
            metadata_cvt[timestamp][10] = payload['pitch']
            data_type_occurrences[timestamp][3] += 1

        if data_type == 'photo':
            metadata_cvt[timestamp][11] = payload['photo_type']
            data_type_occurrences[timestamp][4] += 1

    df_meta = pd.DataFrame(metadata_cvt)
    df_meta = df_meta.transpose()
    df_meta.columns = ['depth', 'temperature', 'longitude', 'latitude', 'altitude', 'distance', 'left', 'right', 'roll', 'yaw', 'pitch', 'photo_type', 'timestamp']
    df_meta.sort_values('timestamp',inplace=True)
    df_meta.index = [i for i in range(df_meta.shape[0])]

    # For debugging
    df_debug = pd.DataFrame(data_type_occurrences)
    df_debug = df_debug.transpose()
    df_debug.columns = ['depth','sonar','gps','attitude','photo','timestamp']
    df_debug.sort_values('timestamp',inplace=True)
    df_debug.index = [i for i in range(df_debug.shape[0])]

    # Convert timestamp to local time
    for n in range(df_meta.shape[0]):
        df_meta['timestamp'][n] = datetime.datetime.fromtimestamp(df_meta['timestamp'][n]).strftime("%A %B %d, %Y %H:%M:%S.%f")

    # --------------------------------------------------------------------------------------------------- #
    # # Old version of log parsing
    # with open(metafile_pth,'r') as f:
    #     lines = f.readlines()[1:]
    #
    # for line in lines:
    #     elements = line.split(",")
    #
    #     # Relevant indices:
    #     # 1 = time
    #     # 2 = depth
    #     # 4 = heading
    #     # 5 = yaw
    #     # 6 = pitch
    #     # 7 = roll
    #
    #     time.append(datetime.datetime.strptime(elements[1].split("time:")[1],"%Y:%m:%d:%H:%M:%S"))
    #     depth.append(float(elements[2].split("depth:")[1][:len(elements[2].split("depth:")[1])-1]))
    #     heading.append(elements[4].split("compass:")[1])
    #     yaw.append(float(elements[5].split("yaw:")[1]))
    #     pitch.append(float(elements[6].split("pitch:")[1]))
    #     roll.append(float(elements[7].split("roll:")[1]))
    #
    # metadata_cvt["time"] = time
    # metadata_cvt["depth"] = depth
    # metadata_cvt["heading"] = heading
    # metadata_cvt["yaw"] = yaw
    # metadata_cvt["pitch"] = pitch
    # metadata_cvt["roll"] = roll

    # return metadata_cvt
    # --------------------------------------------------------------------------------------------------- #

    return df_meta, df_debug

def plot_positional_data(data_pth, save_path, axes, expected_pos=[], expected_vel=0, round_trip=False):

    """
    Plot the expected relative position value for a certain axes. Axis values are
    defined such that x=0, y=1 and z=2

    """

    data_df = pd.read_csv(data_pth)
    data_df = data_df.iloc[14:61,:]

# Data from the CSV file should have columns time, rel_x, rel_y, rel_z and STD

    t_col = pd.to_datetime(data_df["time"]).tolist()
    x_rel = data_df["Relative x"].to_numpy()
    y_rel = data_df["Relative y"].to_numpy()
    z_rel = data_df["Relative z"].to_numpy()+1.37

    t_start = t_col[0]
    delta_t = []

    for n in t_col:
        delta_t.append((n-t_start).total_seconds())

    if (not type(expected_pos) is list) and (not type(expected_pos) is np.ndarray):
        expected = np.array([expected_pos]*len(delta_t))
    else:
        expected = np.array(expected_pos)

    if (len(expected) == 0) and (expected_vel != 0):
        if round_trip:
            forward = np.array([expected_vel*t for t in delta_t[:int(len(delta_t)/2)]])
            backward = np.array([-expected_vel*(delta_t[n]-delta_t[int(len(delta_t)/2)]) for n in range(int(len(delta_t)/2),len(delta_t))])
            backward = backward + forward[-1]
            expected = np.append(forward,backward)
        else:
            expected = np.array([expected_vel*t for t in delta_t])

    fig = plt.figure()
    ax1 = fig.add_subplot(2, 1, 1, label="1")
    ax2 = fig.add_subplot(2, 1, 2, label="2")

    if axes == 0: # Plot x
        ax1.plot(delta_t, x_rel, "bx", markersize=5, label="Collected")
        ax1.plot(delta_t, expected+1.72, color="g", linestyle="-", linewidth=2, label="Expected")
        ax1.set_xlabel('delta time (s)', color='k')
        ax1.set_ylabel('x position (m)', color='k')
        ax1.set_title('Collected position vs expected position')
        ax1.grid(linestyle='--', color='silver')
        ax1.legend(loc='best')

        ax2.plot(delta_t,x_rel-expected-1.72, 'r.', markersize=5, label="Residual")
        ax2.set_xlabel('delta time (s)', color='k')
        ax2.set_ylabel('x position difference (m)', color='k')
        ax2.set_title('Residual plot of expected and collected position')
        ax2.grid(linestyle='--', color='silver')
        ax2.legend(loc='best')

    elif axes == 1: # Plot y
        ax1.plot(delta_t, y_rel, "bx", markersize=5, label="Collected")
        ax1.plot(delta_t, expected, color="g", linestyle="-", linewidth=2, label="Expected")
        ax1.set_xlabel('delta time (s)', color='k')
        ax1.set_ylabel('y position (m)', color='k')
        ax1.set_title('Collected position vs expected position')
        ax1.grid(linestyle='--', color='silver')
        ax1.legend(loc='best')

        ax2.plot(delta_t,y_rel-expected, "r.", markersize=5, label="Residual")
        ax2.set_xlabel('delta time (s)', color='k')
        ax2.set_ylabel('y position difference (m)', color='k')
        ax2.set_title('Residual plot of expected and collected position')
        ax2.grid(linestyle='--', color='silver')
        ax2.legend(loc='best')

    elif axes == 2: # Plot z
        ax1.plot(delta_t, z_rel, "bx", markersize=5, label="Collected")
        ax1.plot(delta_t, expected, color="g", linestyle="-", linewidth=2, label="Expected")
        ax1.set_xlabel('delta time (s)', color='k')
        ax1.set_ylabel('z position (m)', color='k')
        ax1.set_title('Collected position vs expected position')
        ax1.grid(linestyle='--', color='silver')
        ax1.legend(loc='best')

        ax2.plot(delta_t,z_rel-expected, 'r.', markersize=5, label="Residual")
        ax2.set_xlabel('delta time (s)', color='k')
        ax2.set_ylabel('z position difference (m)', color='k')
        ax2.set_title('Residual plot of expected and collected position')
        ax2.grid(linestyle='--', color='silver')
        ax2.legend(loc='best')

    else:
        print("Invalid axis choice")
        return False

    fig.tight_layout()
    fig.savefig(save_path,bbox_inches='tight',format='png',dpi=600)
    plt.close(fig)

    return True

def main():
    DRONE_LENGTH = 0.383 # meters
    DRONE_WIDTH = 0.331 # meters
    DRONE_HEIGHT = 0.143 # meters
    LOCATOR_HEIGHT = 0.121 # meters
    pth = "/Users/jasonyuan/Desktop/Triumf Lab/Drone Testing/June 17 Data/Relative_Positions_delta_x_T1.csv"
    metafile_pth = "/Users/jasonyuan/Desktop/Triumf Lab/Drone Testing/June 17 Data/metafile_delta_x_T1.txt"

    metadata = get_metadata(metafile_pth)
    drone_depth = []

    for n in range(len(metadata["depth"])):
        if (metadata["time"][n].hour == 14) and (metadata["time"][n].minute == 24) and (metadata["time"][n].second == 59):
            break
        drone_depth.append(metadata["depth"][n])

    x_expected = [] # meters
    x_vel = 0.125 # m/s
    y_expected = 1.25+DRONE_LENGTH # meters
    y_vel = 0 # m/s
    z_expected = (sum(drone_depth)/len(drone_depth))-DRONE_HEIGHT/2-LOCATOR_HEIGHT # meters
    z_vel = 0 # m/s

    for i in range(3):
        if i == 0:
            save_path = "/Users/jasonyuan/Desktop/{}_analyzed_plot.png".format("x")
            plot_positional_data(pth, save_path, i, expected_pos=x_expected, expected_vel=x_vel)
        elif i == 1:
            save_path = "/Users/jasonyuan/Desktop/{}_analyzed_plot.png".format("y")
            plot_positional_data(pth, save_path, i, expected_pos=y_expected, expected_vel=y_vel)
        elif i == 2:
            save_path = "/Users/jasonyuan/Desktop/{}_analyzed_plot.png".format("z")
            plot_positional_data(pth, save_path, i, expected_pos=z_expected, expected_vel=z_vel)

if __name__ == "__main__":
    # main()
    df, debug = get_FIFISH_v6_metadata("/Users/jasonyuan/Desktop/Triumf Lab/Drone Testing/July 18 Data/July_18 Log.json")

    # print(df)
    # print(np.array(df['longitude'].to_numpy()))
    # print(type(np.array(df['longitude'].to_numpy())[0]))
    # print(np.isnan(np.array(df['longitude'].to_numpy(),dtype=np.float32)).sum())

    print(debug)
    np_debug = np.array(debug.to_numpy(),dtype=np.double)
    print(debug.shape)

    print(np_debug[:,5][0])
    print(np_debug[:,5][1])
    print(np_debug[:,5][2])
    print(np_debug[:,5][3])

    for n in range(np_debug.shape[1]-1):
        print(n)
        print(np.sum(np_debug[:,n]))
