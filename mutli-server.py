#Multiple connection server implementation
import selectors
import socket
import types
selector = selectors.DefaultSelector()


HOST = "127.0.0.1"
PORT = 65432
lsock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
lsock.bind((HOST,PORT))

print("Listening for connections on ",(HOST,PORT))

#Configure the socket in a non blocking mode
lsock.setblocking(False)

# Register the socket for monitoring with select() and write the events
# Data can be used to track what is sent and received on the socket
selector.register(lsock,selectors.EVENT_READ,data=None)



def accept_wrapper(sock):
    connection,address = sock.accept()
    print("Successful Connection from ",address)
    connection.setblocking(False)
    # Object to hold the data included with the socket
    data = types.SimpleNamespace(address=address,incomingbyte=b'',outgoingbyte=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    selector.register(connection,events,data=data)
    

def service_connection(key,mask):
    socket = key.fileobj
    data = key.data


    #If the socket is ready for reading
    if mask & selectors.EVENT_READ:
        recv_data = socket.recv(1024)
        if recv_data:
            data.outgoingbyte += recv_data
        else:

            print("Closing connection to", data.address)
            # If the client has closed the connection the server should terminate
            selector.unregister(socket)
            socket.close()

    #If the socket is ready for writing
    if mask & selectors.EVENT_WRITE:
        if data.outgoingbyte:
            print("Echoing ",repr(data.outgoingbyte)," to ",data.address)
            sent = socket.send(data.outgoingbyte)
            data.outgoingbyte = data.outb[sent:]

while True:

    # Block untill there are sockets ready for the I/O
    events = selector.select(timeout=None)
    for key,  mask in events:
        if key.data is None:
            accept_wrapper(key.fileobj)
        else:
            service_connection(key,mask)

