import socket

UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind(('', UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print "received message:", data, addr 
    if (data == "CPU TEMP"):
        sendMessage(addr, readCpuTemFile())
    else: break

def sendMessage(addr, message):    
    sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
    sock.sendto(message, (addr, UDP_PORT))    
    
def readCpuTemFile():
#    /sys/class/thermal/thermal_zone0/temp
    with open('/sys/class/thermal/thermal_zone0/temp') as f:
        return f.read()
    

