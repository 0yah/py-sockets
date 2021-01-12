import socket

# Standard loopback interface address
# Can be an IPv4-formatted address string
HOST = "127.0.0.1"  # Localhost

# Port to listen on (non-privileged ports are > 1023)
# Integers between 1-65535
# 1- 1024 are reserved for priviledged users in some systems

PORT = 65432

# Specify the socket type
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    s.bind((HOST, PORT)) # Associate the network interface and port
    s.listen()  # Enables the server to receive connnections
    connection, address = s.accept()
    with connection:
        print("%s has successfully connected" % address)
        while True:
            data = connection.recv(1024)
            if not data:
                break
            connection.sendall(data)#Echos the data received
