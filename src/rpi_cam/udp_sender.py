import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 5656
# MESSAGE = "Hello, World!"

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT
# print "message:", MESSAGE

try:
    sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

    while True:
        MESSAGE = raw_input("Command:")
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

        if MESSAGE == "EXIT":
            break;

finally:
    sock.close()
    print "Socket closed."