import sys
import socket
from pibot import PiBot

UDP_PORT = 5656

def main(args):

    try:
        # Start arthurbot and wait commands from upd port xxxx
        ab = PiBot()
        sock = socket.socket(socket.AF_INET, # Internet
                             socket.SOCK_DGRAM) # UDP
        sock.bind(('', UDP_PORT))
        print "Listening port", UDP_PORT

        while True:
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            print "received message:", data

            # Expexted data is "command (str) units (int), command (str) units (int), ..."
            # Remove commas from string
            data = data.replace(",", "")

            commands = data.split()
            command_len = len(commands)

            for i in range(0, command_len, 2):

                if (commands[i] == "FORWARD" or commands[i] == 'E'):
                    ab.forward(commands[i+1])
                    print data
                elif (commands[i] == "RIGHT" or commands[i] == 'O'):
                    ab.right(commands[i+1])
                    print data
                elif (commands[i] == "LEFT"  or commands[i] == 'V'):
                    ab.left(commands[i+1])
                    print data
                elif (commands[i] == "BACKWARD" or commands[i] == 'T'):
                    ab.backward(commands[i+1])
                    print data
                elif (commands[i] == "EXIT" or commands[i] == 'X'):
                    ab.allStop
                    break
                else:
                    print "Unkown command."

            if (commands[0] == "EXIT" or commands[0] == 'X'):
                ab.allStop
                break

    finally:
        sock.close()
        print "Socket closed."

if __name__ == "__main__":
    main(sys.argv[1:])