import socket
from threading import Thread
from cryptography.fernet import Fernet

class Server:
    Clients = []
    key = Fernet.generate_key()  # Or use a pre-shared key
    cipher = Fernet(key)

    def __init__(self, HOST, PORT):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, PORT))
        self.socket.listen(5)
        print('Server waiting for connection....')
        print(f"Encryption Key (share with clients): {self.key.decode()}")

    def listen(self):
        while True:
            client_socket, address = self.socket.accept()
            print("Connection from: " + str(address))

            client_name = self.receive_message(client_socket)
            client = {'client_name': client_name, 'client_socket': client_socket}

            self.broadcast_message(client_name, f"{client_name} has joined the chat!")
            Server.Clients.append(client)
            Thread(target=self.handle_new_client, args=(client,)).start()

    def handle_new_client(self, client):
        client_name = client['client_name']
        client_socket = client['client_socket']
        while True:
            try:
                client_message = self.receive_message(client_socket)
                if client_message == "bye":
                    self.broadcast_message(client_name, f"{client_name} has left the chat!")
                    Server.Clients.remove(client)
                    client_socket.close()
                    break

                self.broadcast_message(client_name, client_message)
                self.send_message(client_socket, "Your message was received.", acknowledgment=True)

            except (ConnectionResetError, BrokenPipeError):
                self.broadcast_message(client_name, f"{client_name} has left the chat unexpectedly.")
                Server.Clients.remove(client)
                client_socket.close()
                break

    def broadcast_message(self, sender_name, message):
        for client in self.Clients:
            if client['client_name'] != sender_name:
                self.send_message(client['client_socket'], f"{sender_name}: {message}")

    def send_message(self, client_socket, message, acknowledgment=False):
        if acknowledgment:
            message = "ACK:" + message  # Add "ACK:" prefix for acknowledgment messages
        encrypted_message = self.cipher.encrypt(message.encode())
        client_socket.send(encrypted_message)

    def receive_message(self, client_socket):
        encrypted_message = client_socket.recv(1024)
        return self.cipher.decrypt(encrypted_message).decode()

if __name__ == '__main__':
    server = Server('127.0.0.1', 7632)
    server.listen()
