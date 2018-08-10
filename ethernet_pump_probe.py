import socket

ip = "10.33.62.200"
port = 5025

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((ip, devPort))
sock.send(b"*IDN?\n")
print(sock.recv(1024))

