import sys
import socket
from pibot import PiBot

UDP_PORT = 5005

def main(args):

    # Start arthurbot and wait commands from upd port xxxx
    ab = PiBot()
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.bind(('', UDP_PORT))
    print "Listening port", UDP_PORT

    while True:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        print "received message:", data

        # Expexted data is "command units"
        command = data.split()

        if (command[0] == "STOP"):
            ab.allStop()
            print data
        elif (command[0] == "FORWARD"):
            ab.forward(command[1])
            print data
        elif (command[0] == "RIGHT"):
            ab.right(command[1])
            print data
        elif (command[0] == "LEFT"):
            ab.left(command[1])
            print data
        elif (command[0] == "BACKWARD"):
            ab.backward(command[1])
            print data
        elif (command[0] == "EXIT"):
            ab.allStop
            break
        else: break


if __name__ == "__main__":
    main(sys.argv[1:])