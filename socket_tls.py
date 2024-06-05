#!/usr/bin/env python3

"""Implement a TLS handshake from scratch.
"""

import socket
import hashlib
import base64
import os

def server_handshake(connection):
    # Simulate server hello
    server_hello = "ServerHello"
    connection.send(server_hello.encode())

    # Simulate key exchange
    shared_key = base64.b64encode(os.urandom(16)).decode()
    connection.send(shared_key.encode())

    # Simulate finished message
    finished_message = "Finished"
    connection.send(finished_message.encode())

def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 8888))
    server_socket.listen(1)

    print("Server waiting for connection...")
    connection, address = server_socket.accept()

    # Perform handshake
    server_handshake(connection)

    # Simulate data transfer
    data = connection.recv(1024)
    print("Received:", data.decode())

    connection.close()
    server_socket.close()

if __name__ == "__main__":
    ca_cert = "/workspaces/liviaerxin.github.io/attachments/cert/RootCA.crt"
    server_cert = "/workspaces/liviaerxin.github.io/attachments/cert/localhost.crt"
    import socket
    import ssl

    # Client setup
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 8888))

    # TLS setup
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(ca_cert)  # Assuming a self-signed certificate

    # Wrap the connection
    ssl_connection = context.wrap_socket(client_socket, server_hostname='localhost')

    # Send and receive data
    ssl_connection.send("Hello from the client!".encode())
    data = ssl_connection.recv(1024)
    print("Received:", data.decode())

    # Close the connection
    ssl_connection.close()
    client_socket.close()
