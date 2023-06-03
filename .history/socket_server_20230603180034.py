import json
import pickle
import socket
from time import datetime

UDP_IP = "127.0.0.1"
UDP_PORT = 5000


def dict_to_json(data: dict):
    record = {datetime.now(): data}


def run_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.bind(server)
    try:
        while True:
            data, address = sock.recvfrom(1024)
            print(f"Received data: {data.decode()} from: {address}")
            sock.sendto(data, address)
            print(f"Send data: {data.decode()} to: {address}")
            dict = pickle.load(data)
            dict_to_json(dict)

    except KeyboardInterrupt:
        print(f"Destroy server")
    finally:
        sock.close()


if __name__ == "__main__":
    run_server(UDP_IP, UDP_PORT)
