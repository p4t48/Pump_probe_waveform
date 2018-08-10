import socket

ip = "10.33.62.201"
port = 5025

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((ip , port))

qStr = sock.sendall(b'*IDN?')
reply = sock.recv(4096)

print (str(reply))
sock.close()
