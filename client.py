import socket
import threading
from cryptography.fernet import Fernet

# Load AES key
with open("key.key", "rb") as key_file:
    key = key_file.read()

cipher = Fernet(key)

HOST = "127.0.0.1"
PORT = 5555

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# Receive server prompt for name
encrypted_prompt = client.recv(1024)
prompt = cipher.decrypt(encrypted_prompt).decode()
name = input(prompt)
client.send(cipher.encrypt(name.encode()))

def receive_messages():
    while True:
        try:
            encrypted_msg = client.recv(1024)
            message = cipher.decrypt(encrypted_msg).decode()
            print(message)
        except:
            print("❌ Connection closed")
            client.close()
            break

def send_messages():
    while True:
        msg = input()
        full_msg = msg  # client already knows own name
        encrypted_msg = cipher.encrypt(full_msg.encode())
        client.send(encrypted_msg)

receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

send_messages()
