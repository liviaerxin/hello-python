import socket
import selectors

sel = selectors.DefaultSelector()

def accept(server_sock: socket.socket, sel: selectors.BaseSelector, mask):
    # conn: connection socket
    conn, addr = server_sock.accept()  # Should be ready
    print(f"Accept - conn[{conn}] from addr[{addr}]\n")
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, {"type": "connection_socket"})

def read(conn: socket.socket, sel: selectors.BaseSelector, mask):
    data = conn.recv(1024)  # Should be ready
    addr = conn.getpeername()
    print(f"Read - data[{repr(data)}] in conn[{conn}] from addr[{addr}]\n")
    if data:
        conn.sendall(data)  # Hope it won't block
    else:
        # EOF: connection is closed by client
        print(f'Close - conn[{conn}] from addr[{addr}]\n')
        sel.unregister(conn)
        conn.close()

HOST = "127.0.0.1"
PORT = 3234

# server_sock: listening socket
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind((HOST, PORT))
server_sock.listen()
server_sock.setblocking(False)

sel.register(server_sock, selectors.EVENT_READ, {"type": "listening_socket"})

while True:
    print(f"Select register - file descriptors(fds):{list(sel.get_map())}\n")
    events = sel.select()
    for key, mask in events:
        print(f"Select ready - fileobj[{key.fileobj}] fd[{key.fd}], events[{key.events}], data[{key.data}]\n")
        if key.data["type"] == "listening_socket":
            # Handle listening socket
            accept(key.fileobj, sel, mask)
        elif key.data["type"] == "connection_socket":
            # Handle connection socket
            read(key.fileobj, sel, mask)
        else:
            pass