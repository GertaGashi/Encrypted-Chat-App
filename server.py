import socket
import threading
from cryptography.fernet import Fernet

# Load AES key
with open("key.key", "rb") as key_file:
    key = key_file.read()

cipher = Fernet(key)

HOST = "127.0.0.1"
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = {}  # client_socket -> client_name

print("🟢 Server running...")

def handle_client(client):
    while True:
        try:
            encrypted_msg = client.recv(1024)
            if not encrypted_msg:
                break

            message = cipher.decrypt(encrypted_msg).decode()
            sender_name = clients[client]

            print(f"📩 {sender_name}: {message}")

            # Log message
            with open("chat.log", "a") as log:
                log.write(f"{sender_name}: {message}\n")

            # Private message
            if message.startswith("@"):
                try:
                    recipient_name, msg = message[1:].split(" ", 1)
                    found = False
                    for c, n in clients.items():
                        if n == recipient_name:
                            c.send(cipher.encrypt(f"{sender_name} (private): {msg}".encode()))
                            found = True
                            break
                    if not found:
                        client.send(cipher.encrypt(f"❌ User '{recipient_name}' not found.".encode()))
                except ValueError:
                    client.send(cipher.encrypt("❌ Invalid private message format. Use: @name message".encode()))
            else:
                # Broadcast to all except sender
                for c in clients:
                    if c != client:
                        c.send(cipher.encrypt(f"{sender_name}: {message}".encode()))

        except:
            if client in clients:
                print(f"❌ {clients[client]} disconnected")
                del clients[client]
            client.close()
            break

def receive_connections():
    while True:
        client, addr = server.accept()
        client.send(cipher.encrypt("Enter your name: ".encode()))
        name_encrypted = client.recv(1024)
        name = cipher.decrypt(name_encrypted).decode()
        clients[client] = name

        print(f"🔗 Connected: {addr} as {name}")

        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

receive_connections()

