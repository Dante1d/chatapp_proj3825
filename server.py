import socket
from threading import Thread

class Server:
    Clients = []

    # Create a TCP socket over IPv4. Accept at max 5 connections.
    def __init__(self, HOST, PORT):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, PORT))
        self.socket.listen(5)
        print('Server waiting for connection....')

    # Listen for connections on the main thread. When a connection
    # is received, create a new thread to handle it and add the client
    # to the list of clients.
    def listen(self):
        while True:
            client_socket, address = self.socket.accept()
            print("Connection from: " + str(address))
            
            # The first message will be the username
            client_name = client_socket.recv(1024).decode()
            client = {'client_name': client_name, 'client_socket': client_socket}
            
            # Broadcast that the new client has connected
            self.broadcast_message(client_name, client_name + " has joined the chat!")
            
            Server.Clients.append(client)
            Thread(target = self.handle_new_client, args = (client,)).start()

    def handle_new_client(self, client):
        client_name = client['client_name']
        client_socket = client['client_socket']
        while True:
            try:
                # Listen for incoming messages
                client_message = client_socket.recv(1024).decode()
                if not client_message.strip():
                    raise ConnectionResetError

                # If the message is "bye", disconnect the client
                if client_message.strip() == f"{client_name}: bye":
                    self.broadcast_message(client_name, f"{client_name} has left the chat!")
                    Server.Clients.remove(client)
                    client_socket.close()
                    break

                # Broadcast the message to all other clients
                self.broadcast_message(client_name, client_message, receipt=False)
                
                # Send a receipt confirmation back to the sender
                self.broadcast_message(client_name, "Your message was received.", receipt=True)
            except (ConnectionResetError, BrokenPipeError):
                self.broadcast_message(client_name, f"{client_name} has left the chat unexpectedly.")
                Server.Clients.remove(client)
                client_socket.close()
                break

    # Loop through the clients and send the message down each socket.
    # Skip the socket if it's the same client.
    def broadcast_message(self, sender_name, message, receipt=False):
        for client in self.Clients:
            client_socket = client['client_socket']
            client_name = client['client_name']

            if receipt:
                # Send receipt only to the sender
                if client_name == sender_name:
                    client_socket.send(f"Server: {message}".encode())
            else:
                # Send the message to all other clients
                if client_name != sender_name:
                    client_socket.send(message.encode())

if __name__ == '__main__':
  server = Server('127.0.0.1', 7632)
  server.listen()