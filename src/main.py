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
    'Ball Y': 12289,
    'set point X': 12290,
    'set point Y': 12291,
    'in position': 12292,
    'find new path': 12293,
    'new goal point X': 12294,
    'new goal point Y': 12295,
    'valid position': 12296
}
roi_size_x = (143, 543)
roi_size_y = (40, 440)

# Main loop
if __name__ == '__main__':

    # Create objects

    cap = VideoStream(src=0, height=480, width=640)
    client = ModbusClient()
    ball_tracking = BallTracking(capture=cap, watch=False, roi_size_x=roi_size_x, roi_size_y=roi_size_y, color="pink")
    UDP_Client = UDPClient()
    maze_finding = MazeFinder(client=UDP_Client, capture=cap, roi_size_x=roi_size_x, roi_size_y=roi_size_y)

    # get a path from the astar algorithm and send path to plc

    i = 1
    last_pos_state = client.read_int(addresses['in position'])
    prev_time = 0
    path = None
    old_end_point = None

    ball_coordinates = ball_tracking.get_coordinates()
    if ball_coordinates[0] >= 370:
        client.write_int(value=370, address=addresses['set point X'])
    elif ball_coordinates[0] <= 30:
        client.write_int(value=30, address=addresses['set point X'])
    else:
        client.write_int(value=ball_coordinates[0], address=addresses['set point X'])

    if ball_coordinates[1] >= 370:
        client.write_int(value=370, address=addresses['set point Y'])
    elif ball_coordinates[1] <= 30:
        client.write_int(value=30, address=addresses['set point Y'])
    else:
        client.write_int(value=ball_coordinates[1], address=addresses['set point Y'])

    # Send data over Modbus while the Modbus connection is active
    while client.is_connected():
        current_time = time.time()
        ball_coordinates = ball_tracking.get_coordinates()

        client.write_int(value=ball_coordinates[0], address=addresses['Ball X'])
        client.write_int(value=ball_coordinates[1], address=addresses['Ball Y'])
        #print(ball_coordinates)

        new_gp_x = client.read_int(address=addresses['new goal point X'])
        new_gp_y = client.read_int(address=addresses['new goal point Y'])
        new_end_point = (new_gp_x, new_gp_y)

        #print("New end point x: " + str(new_sp_x))
        #print("New end point y: " + str(new_sp_y))
        if new_gp_x <= 30 or new_gp_x >= 370 or new_gp_y <= 30 or new_gp_y >= 370:
            valid_path = False
            client.write_int(address=addresses['valid position'], value=0)
        else:
            valid_path = True
            client.write_int(address=addresses['valid position'], value=1)

        if new_end_point != old_end_point and valid_path:
            path = None
            i = 1

        if client.read_int(addresses['in position']) != last_pos_state:
            print("Searching for path")
            # Set the first path
            if path is None and valid_path:
                path = maze_finding.find_path((ball_coordinates[0], ball_coordinates[1]), new_end_point)
                if path is not None:
                    client.write_int(value=path[1][0], address=addresses['set point X'])
                    client.write_int(value=path[1][1], address=addresses['set point Y'])
                    print("First path found")
                    print(ball_coordinates)
                    print(path)

            # Get a new path
            elif valid_path and path is not None:
                new_path = maze_finding.find_path((ball_coordinates[0], ball_coordinates[1]), (new_gp_x, new_gp_y))
                print(ball_coordinates)
                # if (new_path[1:] == path[i + 1:] and i < len(path) - 1) or new_path is None:
                #     i += 1
                #     if abs(new_path[1][0] - path[i][0]) < 10 and abs(new_path[1][1] - path[i][1]) < 10:
                #         i += 1
                # elif new_path is not None:
                #     i = 1
                #     path = new_path

                print("Old path: " + str(path))
                print("New path: " + str(new_path))
                if new_path is None or new_path == path and new_end_point == old_end_point:
                    if i < len(path) - 1:
                        i += 1
                elif i < len(path) - 1 and new_path[1] == path[i + 1] and new_end_point == old_end_point:
                    i += 1
                elif new_end_point == old_end_point:
                    i = 1
                    path = new_path
                if i >= len(path):
                    i = len(path) - 1

                client.write_int(value=path[i][0], address=addresses['set point X'])
                client.write_int(value=path[i][1], address=addresses['set point Y'])

            # Use the existing path if the new path parameters are illegal
            elif path is not None and not valid_path:
                if i < len(path) - 1:
                    i += 1
                    client.write_int(value=path[i][0], address=addresses['set point X'])
                    client.write_int(value=path[i][1], address=addresses['set point Y'])
                    print("New path invalid")

        last_pos_state = client.read_int(addresses['in position'])
        old_end_point = new_end_point
        # print((current_time - prev_time) * 1000)
        prev_time = current_time
        key = cv2.waitKey(1) & 0xFF
        # If the escape key is pressed, stop the ball tracking.
        if key == 27:
            ball_tracking.stop()
            UDP_Client.close_socket()
            cap.stop()
            client.close()
            break
