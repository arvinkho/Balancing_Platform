import socket
import sys
import json
import numpy as np

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', 1337)
message = 'This is the message.  It will be repeated.'

class client():
    def __init__(self):
        # Create a UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = ('localhost', 1337)
        self.message = 'This is the message.  It will be repeated.'
    def send_data_to_Astar(self,start,goal,maze):
        try:

            # Send data
            maze = maze.tolist()
            data = {}

            data["start"] = start
            data["goal"] = goal
            data["maze"] = maze
            json_data = json.dumps(data)
            print(json_data)
            sent = sock.sendto(json_data.encode(), server_address)
            # Receive response
            print(sys.stderr, 'waiting to receive')
            json_data, server = sock.recvfrom(16384)
            path = json_data.decode()
            if "no path" in path:
                return None
            else:
                path =path.lstrip("[[")
                path = path.rstrip("]]")
                path = path.split("],[")

                decodedpath=[]
                for item in path:
                    str = item.split(",")
                    decodedpath.append((int(str[0]), int(str[1])))
                return decodedpath
        finally:
            print(sys.stderr, 'closing socket')
            sock.close()
