"""
Get position from Water Linked Underwater GPS

Based on the getposition.py script from the Waterlinked UGPS GitHub repo
https://github.com/waterlinked/examples/tree/master

"""
import argparse
import json
import requests
import datetime
import time
import tzlocal
import pandas as pd

def get_data(url):
    try:
        r = requests.get(url)
    except requests.exceptions.RequestException as exc:
        print("Exception occured {}".format(exc))
        return None

    if r.status_code != requests.codes.ok:
        print("Got error {}: {}".format(r.status_code, r.text))
        return None

    return r.json()

def get_antenna_position(base_url):
    return get_data("{}/api/v1/config/antenna".format(base_url))

def get_acoustic_position(base_url):
    return get_data("{}/api/v1/position/acoustic/filtered".format(base_url))

def get_global_position(base_url, acoustic_depth = None):
    return get_data("{}/api/v1/position/global".format(base_url))

def save_to_output_file(df,path):
    df.to_csv(path+"/"+"Relative_Positions.csv")
    return True

def main():
################### Instantiate the argument parser ############################
    parser = argparse.ArgumentParser(description=__doc__)

############ Add the desired arguments that the parser will take in ############
    parser.add_argument(
        "-u",
        "--url",
        help = "Base URL to use",
        type = str,
        default = "http://192.168.7.1")
    parser.add_argument(
        "-a",
        "--antenna",
        action = "store_true",
        help = (
            "Use mid-point of base of antenna as origin for the acoustic " +
            "position. Default origin is the point at sea level directly " +
            "below/above that which the positions of the receivers/antenna " +
            "are defined with respect to"))
    parser.add_argument(
        "-o",
        "--output",
        help="Base path to save output file",
        type=str,
        default=""
    )

    args = parser.parse_args()

############# Print out the input arguments that we are using ##################
    base_url = args.url
    save_path = args.output

    print("Using base_url: %s" % args.url)
    print("Save path is {}".format(save_path))
    print("Using antenna: {}".format(args.antenna))

######################## Get relative position stuff ###########################
    time_list = []
    x_rel_pos = []
    y_rel_pos = []
    z_rel_pos = []
    z_abs_pos = []
    std = []
    position_data = {}

    local = tzlocal.get_localzone()

    start_time = datetime.datetime.now(local)
    time_now = datetime.datetime.now(local)

    while ((time_now-start_time).total_seconds()/3600 < 6):     # Parse while time is less than 6 hours
        time.sleep(0.5)
        acoustic_position = get_acoustic_position(base_url)
        antenna_position = None
        if args.antenna:
            antenna_position = get_antenna_position(base_url)
        depth = None
        time_now = datetime.datetime.now(local)

        if acoustic_position["position_valid"]:
            if antenna_position:
                time_list.append(time_now)
                x_rel_pos.append(acoustic_position["x"] - antenna_position["x"])
                y_rel_pos.append(acoustic_position["y"] - antenna_position["y"])
                z_rel_pos.append(acoustic_position["z"] - antenna_position["depth"])
                z_abs_pos.append(acoustic_position["z"])
                std.append(acoustic_position["std"])

                print(time_now)
                print(acoustic_position)
                print(antenna_position)
                print("Current acoustic position relative to antenna. X: {}, Y: {}, Z: {}".format(
                    acoustic_position["x"] - antenna_position["x"],
                    acoustic_position["y"] - antenna_position["y"],
                    acoustic_position["z"] - antenna_position["depth"]))
            else:
                time_list.append(time_now)
                x_rel_pos.append(acoustic_position["x"])
                y_rel_pos.append(acoustic_position["y"])
                z_rel_pos.append(acoustic_position["z"])
                std.append(acoustic_position["std"])

                print(time_now)
                print("Invalid current acoustic position. X: {}, Y: {}, Z: {}".format(
                    acoustic_position["x"],
                    acoustic_position["y"],
                    acoustic_position["z"]))

            depth = acoustic_position["z"]

######################### Get absolute position stuff ##########################
        global_position = get_global_position(base_url)
        if global_position:
            if depth:
                print("Current global position. Latitude: {}, Longitude: {}, Depth: {}".format(
                    global_position["lat"],
                    global_position["lon"],
                    depth))
            else:
                print("Current global position latitude :{} longitude :{}".format(
                    global_position["lat"],
                    global_position["lon"]))

############################### Saving the data ################################
        position_data["time"] = time_list
        position_data["Relative x"] = x_rel_pos
        position_data["Relative y"] = y_rel_pos
        position_data["Relative z"] = z_rel_pos
        position_data["Absolute z"] = z_abs_pos
        position_data["STD"] = std

        df_position = pd.DataFrame(position_data)

        if save_path:
            save_to_output_file(df_position,save_path)

    return True

if __name__ == "__main__":
    main()
