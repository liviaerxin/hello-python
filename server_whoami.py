"""A simple whoami server to analyze incoming HTTP requests

# For simplicity, we don't do:
# 1. Detect End of HTTP Request either by double CRLF(`\r\n\r\n`) or `Content-Length`.
# 2. Parse the HTTP request message.
# Instead, we just do:
# 1. Read max size of `GET` and `POST` requests data is 4096 bytes.
# 2. Close the connection for each request.
"""

import socket
import selectors
import argparse

sel = selectors.DefaultSelector()

def accept(server_sock: socket.socket, sel: selectors.BaseSelector, mask):
    # conn: connection socket
    conn, addr = server_sock.accept()  # Should be ready
    print(f"Accept - conn[{conn}] from addr[{addr}]\n")
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, {"type": "connection_socket"})

def read(conn: socket.socket, sel: selectors.BaseSelector, mask):
    buffer = conn.recv(4096)
    client_addr = conn.getpeername()
    server_addr = conn.getsockname()
    print(f"Read - data[{repr(buffer)}] in conn[{conn}] from addr[{client_addr}]\n")
    
    if buffer:
        data = buffer.decode("utf-8")
        # Construct HTTP response message
        message =(
            "HTTP/1.1 200 OK\r\n",
            "Content-type: text/html\r\n",
            "Server:localhost\r\n\r\n",
            f"""<!doctype html>
                <html>
                    <body>
                        <h1>Welcome to the server!</h1>
                        <h2>Server address: {server_addr[0]}:{server_addr[1]}</h2>
                        <h3>You're connected through address: {client_addr[0]}:{client_addr[1]}</h3>
                        <body>
                            <pre>{data}<pre>
                        </body>
                    </body>
                </html>""")
    else:
        message = (
            "HTTP/1.1 400 Bad Request\r\n",
            "Content-type: text/html\r\n",
            "Server:localhost\r\n\r\n",
        )
    
    message = "".join(message)
    conn.sendall(message.encode("utf8"))
    
    print(f'Close - conn[{conn}] from addr[{client_addr}]\n')
    sel.unregister(conn)
    conn.close()

def run(host="127.0.0.1", port=3234):
    # server_sock: listening socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((host, port))
    server_sock.listen()
    server_sock.setblocking(False)

    sel.register(server_sock, selectors.EVENT_READ, {"type": "listening_socket"})
    while True:
        print(f"Select register - file descriptors(fds):{list(sel.get_map())}\n")
        # Set timeout for catching `CRTL+C` KeyboardInterrupt
        events = sel.select(2.0)
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

HOST = "127.0.0.1"
PORT = 3234

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='PROG')
    parser.add_argument('-H', '--host', default=HOST)
    parser.add_argument('-P', '--port', default=PORT, type=int)
    
    args = parser.parse_args()
    host = args.host
    port = args.port
    try:
        run(host, port)
    except KeyboardInterrupt:
        # Code to run when Ctrl+C is pressed
        print("\nCtrl+C detected. Exiting gracefully.")