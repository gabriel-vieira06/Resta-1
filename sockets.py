import socket

def get_local_ip():
    local_ip = socket.gethostbyname(socket.gethostname())
    return local_ip

def get_port():
    s = socket.socket()
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port
