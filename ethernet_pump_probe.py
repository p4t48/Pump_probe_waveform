import socket
import random


ip = "10.33.62.201"
port = 5025

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((ip , port))

sock.sendall(b"*IDN?\n")
reply = sock.recv(4096)

print (str(reply))

### THE RESET TOOL ######
sock.sendall(b"*RST\n") #
#########################


## USING USER-DEFINED WAVEFORMS
dpoints = "DATA VOLATILE"
for x in range(100):
    num = str(random.randint(-100,100)/100.)
    dpoints += ", " + num
dpoints += "\n"

#dpoints = "DATA VOLATILE, " + str(1) + ", " + str(.67) + ", " + str(.33) + ", " + str(0) + ", " + str(-.33) + ", " + str(-.67) + ", " + str(-1) + "\n"
#dpoints = "DATA VOLATILE, 1, .67, .33, 0, -.33, -.67, -1\n"

sock.sendall(bytes(dpoints, 'utf-8'))

#sock.sendall(b"DATA VOLATILE, 1, .67, .33, 0, -.33, -.67, -1\n")

sock.sendall(b"FUNC:USER VOLATILE\n")
sock.sendall(b"FUNC USER\n")

sock.sendall(b"FREQ 5 kHZ\n")
sock.sendall(b"VOLT 2 VPP\n")


## USING LOW-LEVEL COMMANDS
#sock.sendall(b"FUNC SQU\n")
#sock.sendall(b"FREQ 5 kHZ\n")
#sock.sendall(b"VOLT 2 VPP\n")
#sock.sendall(b"FUNC:SQU:DCYC 20\n")
#sock.sendall(b"OUTP ON\n")


## USING THE APPLY COMMAND
#sock.sendall(b"APPL:RAMP 5 kHZ, 3.0 VPP, -0.5 V\n")

#sock.sendall(b"APPL:DC DEF, DEF, +0.5 V\n")


## CHECK THE CONFIGURED FUNCTION
sock.sendall(b"FUNC?\n")
print ("FUNC = " + str(sock.recv(4096)))
sock.sendall(b"FREQ?\n")
print ("FREQ = " + str(sock.recv(4096)))
sock.sendall(b"VOLT?\n")
print ("VOLT = " + str(sock.recv(4096))) 
sock.sendall(b"VOLT:UNIT?\n")
print ("[VOLT] = " + str(sock.recv(4096)))
#sock.sendall(b"FUNC:SQU:DCYC?\n")
#print ("Duty Cycle = " + str(sock.recv(4096)) + " %")

sock.sendall(b"OUTP ON\n")
sock.close()
