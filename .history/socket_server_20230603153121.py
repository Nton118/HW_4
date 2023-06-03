import socket


sock = socket.socket()

sock.bind(("", 5000))

sock.listen(1)
