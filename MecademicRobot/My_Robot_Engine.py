"""
    This module defines an interface with the robot

"""

import socket, sys
import time
import threading


class RobotController:
    """Class for the Mecademic Robot allowing for communication and control of the 
    Mecademic Robot with all of its features available

    Attributes:
        Address: IP Address
        socket: socket connecting to physical Mecademic Robot
        End of Block: Setting for EOB reply
        End of Movement: Setting for EOM reply
        Error: Error Status of the Mecademic Robot
    """
    def __init__(self):
        """Constructor for an instance of the Class Mecademic Robot 

        :param address: The IP address associated to the Mecademic Robot
        """
        
        self.address = None
        self.socket = None
        self.EOB = 1
        self.EOM = 1
        self.error = False
        self.queue = False
        self.IP= None
        self.port= None
        self.BUFFER_SIZE = 512  # bytes
        self.TIMEOUT = 0.0       # seconds
        
    def isInError(self):
        """Status method that checks whether the Mecademic Robot is in error mode.
        Returns 1 for error and 0 otherwise.

        :return error: Returns the error flag
        """
        return self.error 


    def send_str(self,msg):
        sent = self.socket.send(bytes(msg+'\0', 'ascii'))
        if sent == 0:
            raise RuntimeError("Robot connection broken")


    def receive_str(self):
        try:
            byte_data = self.socket.recv(self.BUFFER_SIZE)
            if byte_data == b'':
                raise RuntimeError("Robot connection broken")
            return byte_data.decode('ascii')     
        except:
            print('Exception caught')
            return ""

            


    def establish_connection(self, IP, port):
        self.IP=IP
        self.port=port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.
        self.socket.settimeout(self.TIMEOUT)
        sys.stdout.flush()
        self.socket.connect((self.IP, self.port))

    def send_str(self,msg):
        sent = self.socket.send(bytes(msg+'\0', 'ascii'))
        if sent == 0:
            raise RuntimeError("Robot connection broken")        


    def get_response(self):
        robot_answer = ""
        while robot_answer == "":
            robot_answer = self.receive_str()
        print(f'Received: {robot_answer}')
        return 'Received: '+ robot_answer
        sys.stdout.flush()    


    def Disconnect(self):
        """Disconnects Mecademic Robot object from physical Mecademic Robot
        """
        if(self.socket is not None):
            self.socket.close()
            self.socket = None


    def Initialize_Robot(self):
        self.send_str('ResetError')
        time.sleep(1.0)
        self.send_str('ActivateRobot')
        time.sleep(1.0)
        self.send_str('ResetError')
        self.send_str('Home')
        self.send_str('ResetError')
        sys.stdout.flush()        