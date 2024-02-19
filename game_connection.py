import socket
import threading

class Player:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = 0
        self.ip = socket.gethostbyname(socket.gethostname())
        self.client_connected = False
        self.thread = None
        self.play_first = None

    def create_room(self):
        self.client_socket.bind(('', 0))
        self.port = self.client_socket.getsockname()[1]
        threading.Thread(target=self.wait_connection).start()

    def join_room(self, ip, port):
        self.client_socket.connect((ip, port))
        self.port = port
        self.connection = self.client_socket

    def send_message(self, message):
        self.connection.send(message)

    def receive_message(self):
        return self.connection.recv(1024)
    
    def get_host_port(self):
        return self.port
    
    def get_host_ip(self):
        return self.ip

    def wait_connection(self):
        self.client_socket.listen(1)
        self.connection, _ = self.client_socket.accept()
        self.client_connected = True

    def end_connection(self):
        self.client_socket.close()