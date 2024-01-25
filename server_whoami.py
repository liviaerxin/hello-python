import socket
import selectors

sel = selectors.DefaultSelector()

def accept(sock: socket.socket, sel: selectors.BaseSelector, mask):
    conn, addr = sock.accept()  # Should be ready
    print(f"Accept - conn[{conn}] from addr[{addr}]\n")
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, {"type": "data_socket"})

def read(conn: socket.socket, sel: selectors.BaseSelector, mask):
    # For simplicity, 
    # 1. max size of `GET` and `POST` requests data is 4096 bytes
    # 2. close the connection after response
    chunk = conn.recv(4096)
    addr = conn.getpeername()
    print(f"Read - data[{repr(chunk)}] in conn[{conn}] from addr[{addr}]\n")
    
    if chunk:
        data = chunk.decode("utf-8")
        # Construct HTTP response message
        message =(
            "HTTP/1.1 200 OK\r\n",
            "Content-type: text/html\r\n",
            "Server:localhost\r\n\r\n",
            f"""<!doctype html>
                <html>
                    <body>
                        <h1>Welcome to the server!</h1>
                        <h2>Server address: {HOST}:{PORT}</h2>
                        <h3>You're connected through address: {addr[0]}:{addr[1]}</h3>
                        <body>
                            <pre>{data}<pre>
                        </body>
                    </body>
                </html>""")
        message = "".join(message)
        conn.sendall(message.encode("utf8"))
        print(f'Close\n')
        conn.close()
    print(f'Close - conn[{conn}] from addr[{addr}]\n')
    sel.unregister(conn)
    conn.close()

HOST = "127.0.0.1"
PORT = 3234

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen()
sock.setblocking(False)

sel.register(sock, selectors.EVENT_READ, {"type": "listening_socket"})

while True:
    events = sel.select()
    for key, mask in events:
        print(f"Select - fileobj[{key.fileobj}] fd[{key.fd}], events[{key.events}], data[{key.data}]\n")
        if key.data["type"] == "listening_socket":
            # Handle listening socket
            accept(key.fileobj, sel, mask)
        elif key.data["type"] == "data_socket":
            # Handle data socket
            read(key.fileobj, sel, mask)
        else:
            pass