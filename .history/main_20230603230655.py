from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import json
import mimetypes
import pathlib
import pickle
import socket
import threading
import urllib.parse

HOST = "127.0.0.1"
UDP_PORT = 5000
HTTP_PORT = 3000


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        print(pr_url.path)
        if pr_url.path == "/":
            self.send_html_file("index.html")
        elif pr_url.path == "/message":
            self.send_html_file("message.html")
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("error.html", 404)

    def send_to_socket(self, data: dict):
        bytes = pickle.dumps(data)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server = HOST, UDP_PORT
        sock.sendto(bytes, server)
        # sock.close()

    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {
            key: value for key, value in [el.split("=") for el in data_parse.split("&")]
        }
        print(data_dict)
        self.send_to_socket(data_dict)

        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())


def run_http(ip, port):
    server_address = (ip, port)
    http = HTTPServer(server_address, HttpHandler)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


def run_udp(ip, port, data_file):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server = ip, port
    sock.bind(server)
    try:
        while True:
            data, address = sock.recvfrom(1024)
            dict = pickle.loads(data)
            record = {datetime.now(): dict}
            messages = json.load(data_file)
            messages.update(record)
            json.dump(messages, data_file, ensure_ascii=False)

    except KeyboardInterrupt:
        print(f"Destroy server")
    finally:
        sock.close()


if __name__ == "__main__":
    dir_path = pathlib.Path(".")
    if not pathlib.Path().joinpath("storage/data.json").exists():
        stor_path = dir_path / "storage"
        dir_path.mkdir(parents=True, exist_ok=True)
        data_file = open("storage/data.json", "x", encoding="UTF-8")
    data_file = open("storage/data.json", "w", encoding="UTF-8")
    udp_server = threading.Thread(target=run_udp, args=(HOST, UDP_PORT, data_file))
    http_server = threading.Thread(target=run_http, args=(HOST, HTTP_PORT))
    udp_server.start()
    http_server.start()
    udp_server.join()
    http_server.join()
    data_file.close()
