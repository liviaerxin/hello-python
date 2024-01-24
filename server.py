import socket
import selectors

sel = selectors.DefaultSelector()

def accept(sock, mask):
    conn, addr = sock.accept()  # Should be ready
    print('accepted', conn, 'from', addr)
    conn.setblocking(False)
    
    sel.register(conn, selectors.EVENT_READ, read)

def read(conn: socket.socket, mask):
    conn.
    data = conn.recv(1024)  # Should be ready
    if data:
        print('echoing', repr(data), 'to', conn)
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
                            <pre>{data.decode("utf-8")}<pre>
                        </body>
                    </body>
                </html>""")
        message = "".join(message)
        conn.send(message.encode("utf8"))  # Hope it won't block
    else:
        print('closing', conn)
        sel.unregister(conn)
        conn.close()


HOST = "127.0.0.1"
PORT = 3234

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen()
sock.setblocking(False)
sel.register(sock, selectors.EVENT_READ, accept)

while True:
    events = sel.select()
    for key, mask in events:
        callback = key.data
        callback(key.fileobj, mask)