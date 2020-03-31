#!/usr/bin/python3
"""Connect to a Meca500 robot, activate and home it,
send a small program and then close the connection.

Usage:
    python RobotSampleProgram.py
"""

import time
import sys
from threading import Timer

global robot

ROBOT_IP = "192.168.0.100"   # IP of the robot
ROBOT_PORT = 10000           # Communication port


def main_program():
    """Main procedure"""
    global robot
    robot_connect()
    print("Running program main_program...")
    sys.stdout.flush()

    # Set parameters
    robot.run('SetCartAngVel', [80])
    robot.run('SetCartLinVel', [100])
    robot.run('SetJointVel', [10])
    robot.run('SetCartAcc', [10])
    robot.run('SetJointAcc', [10])
    robot.run('SetBlending', [10])
    robot.run('SetAutoConf', [1])
    # Movements
    robot.run('MoveJoints', [-20.000, 10.000, -10.000, 20.000, -10.000, -10.000])
    robot.run('MoveJoints', [20.000, -10.000, 10.000, -20.000, 20.000, -10.000])
    robot.run('MoveJoints', [-20.000, 10.000, -10.000, 20.000, -10.000, -10.000])
    robot.run('MoveJoints', [0.000, -20.000, 20.000, 0.000, 20.000, 0.000])
    robot.wait_for('3012', 'Did not receive EOB')
    robot.run('GetJoints')
    robot.get_response()
    robot.run('Delay', [1])
    robot.run('DeactivateRobot')
    print("Main_program done")
    sys.stdout.flush()


def robot_connect():
    """Establish connection with the robot"""
    global robot
    robot = MecaRobot(ROBOT_IP, ROBOT_PORT)


def robot_disconnect():
    """Establish connection with the robot"""
    global robot
    robot.sock.close()


# ----------- communication class ------------- #
class MecaRobot:
    """Robot class for programming Meca500 robots"""
    def __init__(self, ip, port):
        import socket
        self.BUFFER_SIZE = 512  # bytes
        self.TIMEOUT = 60       # seconds
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self.TIMEOUT)
        print('Connecting to robot %s:%i' % (ip, port))
        sys.stdout.flush()
        self.sock.connect((ip, port))

        # Receive welcome message
        print('Waiting for connection...')
        self.wait_for("3000", "Another user is already connected")
        
        # Reset, activate and home the robot
        self.run('ResetError')
        self.run('ActivateRobot')
        self.wait_for("2000", "Failed to activate the robot")
        self.run('Home')
        self.wait_for("2002", "Failed to home the robot")

    def send_str(self, msg):
        sent = self.sock.send(bytes(msg+'\0', 'ascii'))
        if sent == 0:
            raise RuntimeError("Robot connection broken")

    def receive_str(self):
        byte_data = self.sock.recv(self.BUFFER_SIZE)
        if byte_data == b'':
            raise RuntimeError("Robot connection broken")
        return byte_data.decode('ascii')
        
    def run(self, cmd, values=None):
        if isinstance(values, list):
            str_send = cmd + '(' + (','.join(format(vi, ".6f") for vi in values)) + ')'
        elif values is None:
            str_send = cmd
        else:
            str_send = cmd + '(' + str(values) + ')'

        # Send command to robot
        self.send_str(str_send)

        print('Running: ' + str_send)
        sys.stdout.flush()

    def get_response(self):
        robot_answer = ""
        while robot_answer == "":
            robot_answer = self.receive_str()

        print('Received: %s' % robot_answer)
        sys.stdout.flush()

    def wait_for(self, answer, error_message):
        answer_timer = Timer(10, self.answer_not_found, args=error_message)
        robot_answer = ""

        # loop to find answer, if answer is not found after 10 seconds print error message
        while robot_answer != answer:
            robot_output = self.receive_str()

            if robot_output.find(answer) == -1 & answer_timer.is_alive() is False:
                answer_timer.start()
                answer_timer.join()

            elif robot_output.find(answer) != -1:
                robot_answer = answer

        answer_timer.cancel()
        print('Received: %s' % robot_answer)
        sys.stdout.flush()

    @staticmethod
    def answer_not_found(error_message):
        print(error_message)
        exit(0)


if __name__ == "__main__":
    """Call Main procedure"""
    main_program()

    time.sleep(3)
    print("Closing connection")
    robot_disconnect()
    # Pause execution before closing process (allows users to read last message)
    time.sleep(2)