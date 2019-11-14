#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Locates a ball on the platform with the corresponding
color values and retrieves the X and Y coordinates.
Sends these values to the PLC using Modbus TCP.
IP-address of PLC: 158.38.140.73, port: 503.

@AUTHOR: Arvin Khodabandeh
@DATE: 2019-10-24
"""

import cv2
from image_processing import BallTracking
from modbus_client import ModbusClient
from UDP_client import UDPClient
from maze_finder import MazeFinder
from video_stream import VideoStream
import time

# Addresses for Modbus
addresses = {
    'Ball X': 12288,
    'Ball Y': 12290,
    'set point X': 12292,
    'set point Y': 12294,
    'in position': 12296,
    'find new path': 12298,
    'new set point X': 12300,
    'new set point Y': 12302
}
roi_size_x = (128, 528)
roi_size_y = (40, 440)

# Main loop
if __name__ == '__main__':
    # cap = cv2.VideoCapture(1)
    # cap.set(propId=3, value=640)
    # cap.set(propId=4, value=480)
    # Create objects

    cap = VideoStream(src=1, height=480, width=640)

    client = ModbusClient()
    ball_tracking = BallTracking(capture=cap, watch=False, roi_size_x=roi_size_x, roi_size_y=roi_size_y, color="pink")
    UDP_Client = UDPClient()
    maze_finding = MazeFinder(client=UDP_Client, capture=cap, roi_size_x=roi_size_x, roi_size_y=roi_size_y)
    # get a path from the astar algorithm and send path to plc
    path = maze_finding.find_path((60, 60), (120, 360))

    client.write_int(value=path[0][0], address=addresses['set point X'])
    client.write_int(value=path[0][1], address=addresses['set point Y'])
    # Send data over Modbus while the Modbus connection is active
    i = 1
    last_pos_state = client.read_int(addresses['in position'])
    #prev_time = 0
    while client.is_connected():
        #current_time = time.time()
        ball_coordinates = ball_tracking.get_coordinates()

        client.write_int(value=ball_coordinates[0], address=addresses['Ball X'])
        client.write_int(value=ball_coordinates[1], address=addresses['Ball Y'])

        if client.read_int(addresses['find new path']) > 0:
            print("sleeping")
            new_sp_x = client.read_int(address=addresses['new set point X'])
            new_sp_y = client.read_int(address=addresses['new set point Y'])
            print(new_sp_x)
            print(new_sp_y)
            path = maze_finding.find_path((ball_coordinates[0], ball_coordinates[1]), (new_sp_x, new_sp_y))
            i = 0
            time.sleep(3)


        # print(client.read_int(addresses['in position']))
        if (client.read_int(addresses['in position']) != last_pos_state or i == 0) and path is not None:
            # print(path[i])
            client.write_int(value=path[i][0], address=addresses['set point X'])
            client.write_int(value=path[i][1], address=addresses['set point Y'])
            if i < len(path) - 1:
                i += 1
        #else:
            #print("not reached ")

        #print(str(ball_coordinates))
        last_pos_state = client.read_int(addresses['in position'])
        #print((current_time - prev_time) * 1000)
        #prev_time = current_time
        # key = cv2.waitKey(1) & 0xFF
        # If the escape key is pressed, stop the ball tracking.
        # if key == 27:
        #     ball_tracking.stop()
        #     UDP_Client.close_socket()
        #     cap.stop()
        #     break
