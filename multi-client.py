# Multiple connection client implementation
import selectors
import socket
import types
import sys
selector = selectors.DefaultSelector()


HOST = "127.0.0.1"
PORT = 65432
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((HOST, PORT))

print("Listening for connections on ", (HOST, PORT))

# Configure the socket in a non blocking mode
lsock.setblocking(False)

# Register the socket for monitoring with select() and write the events
# Data can be used to track what is sent and received on the socket
selector.register(lsock, selectors.EVENT_READ, data=None)

messages = [b'Message 1 from client.', b'Message 2 from client.']


def start_connections(host, port, num_conns):
    server_addr = (host, port)
    for i in range(0, num_conns):
        connid = i + 1
        print('Initiating connection', connid, 'with', server_addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(connid=connid,
                                     msg_total=sum(len(m) for m in messages),
                                     recv_total=0,
                                     messages=list(messages),
                                     outb=b'')
        selector.register(sock, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            print("received", repr(recv_data), "from connection", data.connid)
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total == data.msg_total:
            print("closing connection", data.connid)
            selector.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print("sending", repr(data.outb), "to connection", data.connid)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]


#Get console arguments
if len(sys.argv) != 4:
    print("usage:", sys.argv[0], "<host> <port> <num_connections>")
    sys.exit(1)

host, port, num_conns = sys.argv[1:4]
start_connections(host, int(port), int(num_conns))


while True:
    events = selector.select(timeout=1)
    if events:
        for key, mask in events:
            service_connection(key, mask)
    # Check for a socket being monitored to continue.
    if not selector.get_map():
        break
