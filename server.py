import socket
import threading
import json
import hashlib
import cryptography
from cryptography.fernet import Fernet

host = "127.0.0.1"
port = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

sessionUsers = []
nicknames = []



def read_user_registry(file_path):
    user_registry = {}
    with open(file_path, 'r') as file:
        for line in file:
            user, hashed_password = line.strip().split(':')
            user_registry[user] = hashed_password
    return user_registry

userRegistry = read_user_registry('hashed_passwords.txt')
onlineUsers = {}

private_chats = {}

def get_online_users(client_identity):
    online_list = []
    for key in onlineUsers.keys():
        if onlineUsers[key] != client_identity:
            online_list.append(key)
    serialized_list = json.dumps(online_list).encode()
    return serialized_list

def broadcast(message, sender):
    for client in sessionUsers:
        if client != sender:
            client.send(message)

def handle_private_chat(client, recipient):
    while True:
        try:
            message = client.recv(1024)
            private_chats[recipient].send(message)
        except:
            break

def create_session_key():
    key=Fernet.generate_key()
    print(key)
    return key

def handle(client):
    in_private_chat = False
    private_chat_partner = None
    while True:
        try:
            message = client.recv(1024)
            string_message = message.decode()
            list_message = string_message.split()

            if list_message[0] == 'ONLINE':
                online_list = get_online_users(client)
                client.send(online_list)

            elif list_message[0] == 'INVITE':
                recipient = list_message[1]
                if recipient in onlineUsers:
                    onlineUsers[recipient].send(f'INVITE {nicknames[sessionUsers.index(client)]}'.encode('ascii'))

            elif list_message[0] == 'ACCEPT':
                sender = list_message[1]
                if sender in onlineUsers:
                    private_chats[client] = onlineUsers[sender]
                    private_chats[onlineUsers[sender]] = client
                    in_private_chat = True
                    private_chat_partner = onlineUsers[sender]
                    session_key = create_session_key()

                    onlineUsers[sender].send(f'SESSIONKEY '.encode('ascii'))
                    onlineUsers[sender].send(session_key)
                    client.send(f'SESSIONKEY '.encode('ascii'))
                    client.send(session_key)
            elif list_message[0] == 'ENDCHAT':
                in_private_chat = False
                private_chat_partner = None

            elif in_private_chat:
                # If in a private chat, send the message to the other chat participant.
                private_chat_partner.send(message)

            else:
                broadcast(message, client)

        except:
            index = sessionUsers.index(client)
            sessionUsers.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} left the chat!'.encode('ascii'), None)
            onlineUsers.pop(nickname)
            nicknames.remove(nickname)
            break


def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        hashed_password = client.recv(1024).decode('ascii')

        if nickname in userRegistry and userRegistry[nickname] == hashed_password:
            print(f'{nickname} is now online in the server!')
            onlineUsers[nickname] = client
            nicknames.append(nickname)

            client.send('USERLIST'.encode('ascii'))
            client.send('LISTDATA'.encode('ascii'))

            serialized_list = get_online_users(client)
            client.send(serialized_list)

            sessionUsers.append(client)
            broadcast(f'{nickname} joined the chat!'.encode('ascii'), client)
            client.send('Connected to the server!\n\tIf you would like to invite, type "INVITE"'.encode('ascii'))

            thread = threading.Thread(target=handle, args=(client,))
            thread.start()

        else:
            print(f'{nickname} exists, but the password is incorrect')
            client.send('RESTART'.encode('ascii'))


print("Server is listening..")
receive()
