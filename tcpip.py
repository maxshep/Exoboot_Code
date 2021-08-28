import socket
import select


class ServerTCP(object):
    def __init__(self, server_ip, recv_port):
        self.SERVER_IP = server_ip
        self.RECV_PORT = recv_port
        self.recv_conn = 0.

    def close(self):
        self.recv_conn.close()

    def from_client(self):
        if select.select([self.recv_conn], [], [], 0.0001)[0]:
            return self.recv_conn.recv(8192).decode()
        else:
            return ''

    def to_client(self, msg):
        self.recv_conn.sendall(msg.encode())
        return

    def start_server(self):
        recv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        recv_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        recv_socket.bind((self.SERVER_IP, self.RECV_PORT))
        recv_socket.listen(1)
        print('\nWaiting for client to connect.')
        self.recv_conn, recv_addr = recv_socket.accept()
        recv_socket.close()
        print('Client connected!')
        return


class ClientTCP(object):
    def __init__(self, server_ip, recv_port):
        self.SERVER_IP = server_ip
        self.RECV_PORT = recv_port
        self.recv_conn = 0.
        self.start_client()

    def close(self):
        self.recv_conn.close()

    def from_server(self):
        if select.select([self.recv_conn], [], [], 0.0001)[0]:
            return self.recv_conn.recv(8192).decode()
        else:
            return ''

    def to_server(self, msg):
        self.recv_conn.sendall(msg.encode())
        return

    def start_client(self):
        self.recv_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recv_conn.connect((self.SERVER_IP, self.RECV_PORT))


if __name__ == "__main__":
    print("Testing client.")
    client = ClientTCP('192.168.1.2', 8080)
    client.to_server('!TEST')

    while True:
        msg = client.from_server()
        if any(msg):
            print(f"Received: {msg}")
            break
