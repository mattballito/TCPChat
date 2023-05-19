import socket
import threading
import json
import hashlib

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

def broadcast(message):
    for client in sessionUsers:
        client.send(message)

def getOnlineUsers(clientIdentity):
    onlineList = []
    for key in onlineUsers.keys():
        if (onlineUsers[key] != clientIdentity):
            onlineList.append(key)
    serialized_list = json.dumps(onlineList).encode()
    return serialized_list

from cryptography.fernet import Fernet

chat_keys = {}  # dictionary to store chat keys

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            stringMessage = message.decode()
            listMessage = stringMessage.split()

            if listMessage[0] == "CHATWITH":  # if "CHATWITH" command is in the message
                user_to_chat_with = listMessage[1]

    # generate a symmetric key
                key = Fernet.generate_key()
                chat_keys[frozenset([client, onlineUsers.get(user_to_chat_with)])] = key
                print({key})

            elif listMessage[0] == "ONLINE":
                onlineList = getOnlineUsers(client)
                client.send(onlineList)

            else:
                broadcast(message)
        except:
            index = sessionUsers.index(client)
            sessionUsers.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} left the chat!'.encode('ascii'))
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
        if (str(nickname) in userRegistry):
            if (userRegistry[f'{nickname}'] == hashed_password):
                print(f'{nickname} is now online in the server!')
                onlineUsers[nickname] = client
                print("SERVER: this is dict:", onlineUsers)
                nicknames.append(nickname)

                client.send('USERLIST'.encode('ascii'))
                client.send('LISTDATA'.encode('ascii'))

                serialized_list = getOnlineUsers(client)
                client.send(serialized_list)

                sessionUsers.append(client)
                broadcast(f'{nickname} joined the chat!'.encode('ascii'))
                thread = threading.Thread(target=handle, args=(client,))
                thread.start()
            else:
                print(f'{nickname} exists, but password is incorrect')
                client.send('RESTART'.encode('ascii'))
        else:
            print("No such user exists in registry.")
            client.send('RESTART'.encode('ascii'))

print("Server is listening..")
receive()
