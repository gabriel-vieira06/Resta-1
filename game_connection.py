import socket
import threading

class Server:
    def __init__(self):
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = 0
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_thread = threading.Thread(target=self.start)
        self.client_connected = False

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.port = self.server_socket.getsockname()[1]
        self.server_socket.listen(1)

        print(f"Server listening on {self.host}:{self.port}")

        try:
            client_socket, client_address = self.server_socket.accept()
            print(f"Connection from {client_address}")
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            client_thread.start()
            self.client_connected = True
        except OSError:
            print("Server socket closed. Stopping...")

    def start_server(self):
        self.server_thread.start()

    def handle_client(self, client_socket, client_address):
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    print(f"Client {client_address} disconnected")
                    self.client_connected = False
                    break
                print(f"Received data from {client_address}: {data.decode()}")
                # Aqui você pode adicionar lógica para processar os dados recebidos do cliente
            except ConnectionResetError:
                print(f"Client {client_address} forcibly disconnected")
                self.client_connected = False
                break
        client_socket.close()

    def stop(self):
        self.server_socket.close()
        
class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket_client = None
        self.thread = None
        self.connected = False

    def connect(self):
        try:
            self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_client.connect((self.host, self.port))
            self.connected = True
            print("Connected to the server.")
            self.thread = threading.Thread(target=self.activity)
            self.thread.start()
        except Exception as e:
            print(f"Error on connection: {e}")

    def activity(self):
        while self.connected:
            try:
                data = self.socket_client.recv(1024)
                if not data:
                    print("Disconnected from the server.")
                    break
                print("Message from server:", data.decode())
            except Exception as e:
                print(f"Error on activity: {e}")
                break

    def send_message(self, message):
        if self.connected:
            try:
                self.socket_client.sendall(message.encode())
            except Exception as e:
                print(f"Error on sending message: {e}")

    def disconnect(self):
        if self.connected:
            self.connected = False
            self.thread.join()
            self.socket_client.close()
            print("Disconnected from server.")


