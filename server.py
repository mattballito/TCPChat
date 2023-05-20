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

private_chats = {}

def getOnlineUsers(clientIdentity):
    onlineList = []
    for key in onlineUsers.keys():
        if (onlineUsers[key] != clientIdentity):
            onlineList.append(key)
    serialized_list = json.dumps(onlineList).encode()
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

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            stringMessage = message.decode()
            listMessage = stringMessage.split()

            if (listMessage[1] == "ONLINE"):
                onlineList = getOnlineUsers(client)
                client.send(onlineList)
            elif (listMessage[1] == "INVITE"):
                recipient = listMessage[2]
                if recipient in onlineUsers:
                    onlineUsers[recipient].send(f'INVITE {nicknames[sessionUsers.index(client)]}'.encode('ascii'))
            elif (listMessage[1] == "ACCEPT"):
                sender = listMessage[2]
                if sender in onlineUsers:
                    private_chats[client] = onlineUsers[sender]
                    private_chats[onlineUsers[sender]] = client
                    thread = threading.Thread(target=handle_private_chat, args=(client, onlineUsers[sender]))
                    thread.start()
                    thread = threading.Thread(target=handle_private_chat, args=(onlineUsers[sender], client))
                    thread.start()
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
                broadcast(f'{nickname} joined the chat!'.encode('ascii'), client) #Add client as sender
                client.send('Connected to the server!\n\tIf you would like to invite, type "INVITE"'.encode('ascii'))
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
