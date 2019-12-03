import socket
import sys
import json

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', 1337)
message = 'This is the message.  It will be repeated.'
"""
    A UDP Client, that sends a json object containgin an int matrix, and two int arrays to a local UDP server
    and wait for an int array as a response.
    :author  :  Fredborg.
    :version : 1
"""
class UDPClient(object):

    def __init__(self):
        '''
        generates a UDP socet with a local host on port 1337
        '''
        # Create a UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = ('localhost', 1337)


    def send_data_to_Astar(self, maze, start, goal):
        '''
        send's the maze it recived to a UDP server
        :param maze: the maze to be inspected and solved.
        :param start: the start of the maze.
        :param goal: the end of the maze.
        :return:
        '''
        try:
            #build a JSON object
            maze = maze.tolist()
            data = {}

            data["start"] = start
            data["goal"] = goal
            data["maze"] = maze

            json_data = json.dumps(data)

            #send data to server
            self.sock.sendto(json_data.encode(), self.server_address)


            # Receive response
            print(sys.stderr, 'waiting to receive')
            json_data, server = self.sock.recvfrom(16384)
            path = json_data.decode()
            # Check that the response is a valid path.

            # If the path is no path return none
            if "no path" in path:
                return None

            # else return the solved path
            else:
                path = json.loads(path)
                return path
        # in case of error print message and close socket
        except:
            print(sys.stderr, 'closing socket')
            self.sock.close()

    def close_socket(self):
        '''
        closes the socket that the UDP client is using to send data.
        :return:
        '''
        print(sys.stderr, 'closing socket')
        self.sock.close()
