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
# Addresses for Modbus
addresses = {
    'Ball X': 12288,
    'Ball Y': 12290,
    'Point X': 12292,
    'Point Y': 12294,
}
dimentions = 640,480
# Main loop
if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    cap.set(propId=3, value=dimentions[0])
    cap.set(propId=4, value=dimentions[1])

    # Create objects

    client = ModbusClient()
    ball_tracking = BallTracking(capture=cap, watch=True, color="pink")
    maze_finding = Maze_Finder()
    UDP_Client = UDP_Client()
    # get a path from the astar algorythm and send path to plc
    path = maze_finding.findPath(False,cap,dimentions,ball_tracking.get_coordinates(), (dimentions[0]-1, dimentions[1]-1))
    for points in path:
        x= points[0]
        y= points[1]
        client.write_int(value=x,address=addresses['Point X'])
        client.write_int(value=y,address=addresses['Point Y'])
    # Send data over Modbus while the Modbus connection is active
    while client.is_connected():
        ball_coordinates = ball_tracking.get_coordinates()
        client.write_int(value=ball_coordinates[0], address=addresses['Ball X'])
        client.write_int(value=ball_coordinates[1], address=addresses['Ball Y'])
        
        key = cv2.waitKey(10) & 0xFF
        # If the escape key is pressed, stop the ball tracking.
        if key == 27:
            ball_tracking.stop()
            break