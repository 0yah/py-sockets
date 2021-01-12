import socket


HOST = "127.0.0.1"
PORT = 65432

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
    s.connect((HOST,PORT))
    s.sendall(b"Hello World")# Transmits the string to the server as bytes
    data = s.recv(1024) # Receives the servers data and the maximum amount of data to be received at a time(Buffer)

print("Received",repr(data))