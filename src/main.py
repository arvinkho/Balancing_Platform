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
from UDP_client import UDP_Client
from maze_finder import Maze_Finder
import threading

# Addresses for Modbus
addresses = {
    'Ball X': 12288,
    'Ball Y': 12290,
    'set point X': 12292,
    'set point Y': 12294,
    'in position': 12296
}
dimentions = (640, 480)

# Main loop
if __name__ == '__main__':
    cap = cv2.VideoCapture(1)
    cap.set(propId=3, value=640)
    cap.set(propId=4, value=dimentions[1])

    # Create objects

    client = ModbusClient()
    ball_tracking = BallTracking(capture=cap, watch=True, color="pink")
    maze_finding = Maze_Finder()
    UDP_Client = UDP_Client()

    # get a path from the astar algorythm and send path to plc
    path = maze_finding.findPath(UDP_Client, cap, (ball_tracking.get_coordinates()), (350, 100))

    client.write_int(value=path[0][0], address=addresses['set point X'])
    client.write_int(value=path[0][1], address=addresses['set point Y'])

    # Send data over Modbus while the Modbus connection is active
    i = 1
    last_pos_state = client.read_int(addresses['in position'])
    while client.is_connected():
        ball_coordinates = ball_tracking.get_coordinates()
        client.write_int(value=ball_coordinates[0], address=addresses['Ball X'])
        client.write_int(value=ball_coordinates[1], address=addresses['Ball Y'])
        print(client.read_int(addresses['in position']))
        if client.read_int(addresses['in position']) != last_pos_state:
            print(path[i])
            client.write_int(value=path[i][1], address=addresses['set point X'])
            client.write_int(value=path[i][0], address=addresses['set point Y'])
            if i < len(path) - 1:
                i += 1
        else:
            print("not reached ")

        last_pos_state = client.read_int(addresses['in position'])
        key = cv2.waitKey(50) & 0xFF
        # If the escape key is pressed, stop the ball tracking.
        if key == 27:
            ball_tracking.stop()
            break
