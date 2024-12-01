import socket
from threading import Thread
from cryptography.fernet import Fernet

class Client:
    def __init__(self, HOST, PORT):
        self.socket = socket.socket()
        self.socket.connect((HOST, PORT))
        self.key = input("Enter the encryption key: ").encode()
        self.cipher = Fernet(self.key)
        self.name = input("Enter your name: ")
        self.send_message(self.name)  # Send username to the server
        Thread(target=self.receive_message).start()
        self.send_message_loop()

    def send_message(self, message):
        encrypted_message = self.cipher.encrypt(message.encode())
        self.socket.send(encrypted_message)

    def send_message_loop(self):
        while True:
            message = input("")
            self.send_message(message)
            if message == "bye":
                break

    def receive_message(self):
      while True:
          try:
              encrypted_message = self.socket.recv(1024)
              message = self.cipher.decrypt(encrypted_message).decode()

              # Check if the message is an acknowledgment
              if message.startswith("ACK:"):
                  # Remove the "ACK:" prefix and display the message in green
                  print("\033[1;32;40m" + message[4:] + "\033[0m")
              else:
                  # Display regular messages in red
                  print("\033[1;31;40m" + message + "\033[0m")
          except:
              print("Disconnected from server.")
              break


if __name__ == '__main__':
    Client('127.0.0.1', 7632)
