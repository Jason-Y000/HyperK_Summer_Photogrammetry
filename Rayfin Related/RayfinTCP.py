"""
TCP port communication with Rayfin camera
"""

import os
import socket
import argparse
import time
import binascii
from contextlib import closing

# Connection details and message setup
CAM_IP = None
TCP_PORT = 8888  # From Rayfin manual for camera control
BUFFER_SIZE = 1024

PIC = "TakePicture"
LOG = "StartLogging"
STOP_LOG = "StopLogging"
PIC_LOG = "LogDataOnStill"
ZERO_IMU = "SetIMUZero"
CHECK_LOG = "IsLogging"
ROLL = "Roll"
TILT = "Tilt"

commands_dict = {"P":PIC,"L":LOG,"PL":PIC_LOG,"Z":ZERO_IMU,"C":CHECK_LOG,
                "T":TILT, "R":ROLL, "SL":STOP_LOG}

def get_TCP_message(message):
    hex_val = message.encode('ascii').hex()     # Convert to hex string

    # Add TCP message header and padding
    message_length = len(message)
    hex_len = hex(message_length)[2:]

    if len(hex_len) < 2:
        hex_len = '0' + hex_len    # Make the length a pair

    hex_packet = hex_len + '000000' + hex_val

    # Get the byte packet
    # byte_packet = bytes.fromhex(hex_packet)
    byte_packet = binascii.unhexlify(hex_packet)

    return byte_packet

def checkPort(ip, port):
    with closing(socket.socket(socket.AF_INET,socket.SOCK_STREAM)) as sock:
        if sock.bind((ip, port)) == 0:
            print("Port open")
            return True
        else:
            print("Port closed")
            return False

def initPort(ip, port):
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect((ip,port))

    return sock

def send_receiveData(sock,message,buffer):
    sock.send(message)
    time.sleep(0.1)
    data = sock.recv(buffer)
    sock.close()

    return data

def main():

######################## Argument parsing ##############################
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "-i",
        "--IP",
        help = "IP address of the Rayfin camera",
        type = str,
        default = "")

    parser.add_argument(
        "-p",
        "--port",
        help = "TCP port for camera control",
        type = int,
        default = 8888)

    args = parser.parse_args()

################## Check if the camera IP is provided ##################
    if args.IP == "":
        print("Rayfin IP address is missing. Cannot connect")
        return False
    else:
        CAM_IP = args.IP

    TCP_PORT = args.port

################# Port check and then connection ###################
    if not checkPort(CAM_IP,TCP_PORT):
        print("Port cannot be connected to, or is not open. Check")
        return False

####### For testing, list out the different types of queries and try ########
    command = "Test"
    while command.lower() != 'q':
        print(commands_dict.keys())
        command = input("Choose one of the above commands: ")

        if command not in commands_dict.keys():
            continue

        message = get_TCP_message(commands_dict[command])
        sock = initPort(CAM_IP,TCP_PORT)
        data = send_receiveData(sock, message, BUFFER_SIZE)

        print("Data received from previous command: ",data)

    return True

if __name__ == "__main__":
    main()
