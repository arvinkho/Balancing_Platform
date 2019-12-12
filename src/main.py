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
    'path not found': 12296
}
roi_size_x = (150, 550)
roi_size_y = (45, 445)

# Main loop
if __name__ == '__main__':

    # SET TRUE TO DISPLAY SAMPLE TIME
    timing = False

    # Create objects

    cap = VideoStream(src=1, height=480, width=640)
    client = ModbusClient()
    ball_tracking = BallTracking(capture=cap, watch=False, roi_size_x=roi_size_x, roi_size_y=roi_size_y, color="pink")
    UDP_Client = UDPClient()
    maze_finding = MazeFinder(client=UDP_Client, capture=cap, roi_size_x=roi_size_x, roi_size_y=roi_size_y)

    # Create variables to be used



    i = 1
    last_pos_state = client.read_int(addresses['in position'])
    prev_time = 0
    path = None
    old_end_point = None

    ball_coordinates = ball_tracking.get_coordinates()
    ball_tracking.watch_frame()

    # Set the initial set point to the balls current position. If the ball
    # position is illegal, set the set points to the max or min legal values.
    if ball_coordinates[0] >= 365:
        client.write_int(value=365, address=addresses['set point X'])
    elif ball_coordinates[0] <= 35:
        client.write_int(value=35, address=addresses['set point X'])
    else:
        client.write_int(value=ball_coordinates[0], address=addresses['set point X'])

    if ball_coordinates[1] >= 365:
        client.write_int(value=365, address=addresses['set point Y'])
    elif ball_coordinates[1] <= 35:
        client.write_int(value=35, address=addresses['set point Y'])
    else:
        client.write_int(value=ball_coordinates[1], address=addresses['set point Y'])

    # Send data over Modbus while the Modbus connection is active
    while client.is_connected():

        if timing:
            current_time = time.time()

        ball_coordinates = ball_tracking.get_coordinates()

        client.write_int(value=ball_coordinates[0], address=addresses['Ball X'])
        client.write_int(value=ball_coordinates[1], address=addresses['Ball Y'])

        new_gp_x = client.read_int(address=addresses['new goal point X'])
        new_gp_y = client.read_int(address=addresses['new goal point Y'])
        new_end_point = (new_gp_x, new_gp_y)

        # Checks if the new goal points are in the valid range
        if new_gp_x < 35 or new_gp_x > 365 or new_gp_y < 35 or new_gp_y > 365:
            valid_end_points = False
        else:
            valid_end_points = True

        # if the the end points are changed and the new endpoints are valid
        if new_end_point != old_end_point and valid_end_points:
            path = None
            i = 1

        # The ball is in position, find a new path
        current_pos_state = client.read_int(addresses['in position'])
        if current_pos_state != last_pos_state:
            print("Searching for path")

            if path is not None and path[i] == path[-1]:
                client.write_int(value=new_end_point[0], address=addresses['set point X'])
                client.write_int(value=new_end_point[1], address=addresses['set point Y'])

            # Set the first path
            elif path is None and valid_end_points:
                path = maze_finding.find_path((ball_coordinates[0], ball_coordinates[1]), new_end_point)
                if path is not None:
                    client.write_int(value=path[1][0], address=addresses['set point X'])
                    client.write_int(value=path[1][1], address=addresses['set point Y'])
                    client.write_int(value=0, address=addresses['path not found'])
                    print("First path found")
                    print(ball_coordinates)
                    print(path)
                else:
                    client.write_int(value=1, address=addresses['path not found'])

            # Get a new path
            elif valid_end_points and path is not None:
                new_path = maze_finding.find_path((ball_coordinates[0], ball_coordinates[1]), (new_gp_x, new_gp_y))
                print("Old path: " + str(path))
                print("New path: " + str(new_path))

                # If the new path is not found or the new path is the same as the old
                # path, increment the old path
                if new_path is None or new_path == path and new_end_point == old_end_point:
                    if i < len(path) - 1:
                        i += 1

                # If the next position in the old path is the same as the first position in the
                # new path, increment the old path
                elif i < len(path) - 1 and new_path[1] == path[i + 1] and new_end_point == old_end_point:
                    i += 1

                # Replace the old path with the new one
                elif new_end_point == old_end_point:
                    i = 1
                    path = new_path

                if i >= len(path):
                    i = len(path) - 1

                client.write_int(value=path[i][0], address=addresses['set point X'])
                client.write_int(value=path[i][1], address=addresses['set point Y'])

            # Use the existing path if the new path parameters are illegal
            elif path is not None and not valid_end_points:
                if i < len(path) - 1:
                    i += 1
                    client.write_int(value=path[i][0], address=addresses['set point X'])
                    client.write_int(value=path[i][1], address=addresses['set point Y'])
                    print("New path invalid")

        last_pos_state = current_pos_state
        old_end_point = new_end_point

        # Display the cycle time
        if timing:
            print("Time elapsed: " + str((current_time - prev_time) * 1000) + " ms")
            prev_time = current_time

        key = cv2.waitKey(1) & 0xFF

        # If the space key is pressed, update the image window with the most recent frame
        if key == 32:
            ball_tracking.watch_frame()

        # If the escape key is pressed, stop the ball tracking.
        if key == 27:
            ball_tracking.stop()
            UDP_Client.close_socket()
            cap.stop()
            client.close()
            break
