import socket, sys, time
from threading import Timer
class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

def send_str(msg, sock):
    sent = sock.send(bytes(msg+'\0', 'ascii'))
    if sent == 0:
        raise RuntimeError("Robot connection broken")

def receive_str(sock,BUFFER_SIZE):
    byte_data = sock.recv(BUFFER_SIZE)
    if byte_data == b'':
        raise RuntimeError("Robot connection broken")
    return byte_data.decode('ascii')

def get_response(sock,BUFFER_SIZE):
    robot_answer = ""
    while robot_answer == "":
        robot_answer = receive_str(sock,BUFFER_SIZE)

    print('Received: %s' % robot_answer)
    sys.stdout.flush()    


def run(cmd, values=None):
    if isinstance(values, list):
        str_send = cmd + '(' + (','.join(format(vi, ".6f") for vi in values)) + ')'
    elif values is None:
        str_send = cmd
    else:
        str_send = cmd + '(' + str(values) + ')'

    return str_send

def Timer_trial_func():
    print('Timer is executed')

if __name__ == "__main__":
    ip = "192.168.0.100"   # IP of the robot
    port = 10000           # Communication port
    BUFFER_SIZE = 512  # bytes
    TIMEOUT = 60       # seconds
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)
    print('Connecting to robot %s:%i' % (ip, port))
    sys.stdout.flush()
    sock.connect((ip, port))
    local_timer=RepeatTimer(0.1, get_response,[sock,BUFFER_SIZE])    
    local_timer.start()    
    print("Socket connected...")
    send_str('ResetError',sock)
    time.sleep(1.0)
    send_str('ActivateRobot',sock)
    time.sleep(1.0)
    send_str('ResetError',sock)
    send_str('Home',sock)
    send_str('ResetError',sock)
    sys.stdout.flush()
    for cycle in range(10):
        cmnd= run('MoveJoints', [-20.000, 10.000, -10.000, 20.000, -10.000, -10.000])
        send_str(cmnd,sock)
        time.sleep(1.0)
        cmnd= run('MoveJoints', [20.000, -10.000, 10.000, -20.000, 20.000, -10.000])
        send_str(cmnd,sock)
        time.sleep(1.0)
        cmnd= run('MoveJoints', [-20.000, 10.000, -10.000, 20.000, -10.000, -10.000])
        send_str(cmnd,sock)
        time.sleep(1.0)
        cmnd= run('MoveJoints', [0.000, -20.000, 20.000, 0.000, 20.000, 0.000])
        send_str(cmnd,sock)
        time.sleep(1.0)  
    # time.sleep(5.0)  
    # send_str('DeactivateRobot',sock)
    # print('Prepare for brakes release')
    # time.sleep(5.0)  
    # send_str('BrakesOff',sock)
    # time.sleep(15.0)  
    # send_str('BrakesOn',sock)  
    # send_str('ActivateRobot',sock)
    local_timer.cancel()      
    print("Finished...")
    exit(0)

