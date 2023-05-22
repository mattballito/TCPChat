import socket
import threading
import json
import hashlib
import cryptography
from cryptography.fernet import Fernet
import rsa

host = "127.0.0.1"
port = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

sessionUsers = []
nicknames = []

public_keys = {
    "user1": "publicKey1.pem",
    "user2": "publicKey2.pem",
    "user3": "publicKey3.pem"
}


def read_user_registry(file_path):
    user_registry = {}
    with open(file_path, 'r') as file:
        for line in file:
            user, hashed_password = line.strip().split(':')
            user_registry[user] = hashed_password
    return user_registry


userRegistry = read_user_registry('hashed_passwords.txt')
onlineUsers = {}


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


def create_session_key():
    key = Fernet.generate_key()
    print("session key for private chat generated:", key)
    return key


def load_Key(file):
    with open(file, 'rb') as p:
        publicKey = rsa.PublicKey.load_pkcs1(p.read())
    return publicKey


def encrypt(message, key):
    return rsa.encrypt(message, key)


def handle(client):
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
                originUsername = list_message[2]
                if recipient in onlineUsers:
                    onlineUsers[recipient].send(f'INVITATION {originUsername}'.encode('ascii'))

            elif list_message[0] == 'ACCEPT':
                sender = list_message[1]
                originUsername = list_message[2]

                if originUsername in onlineUsers and sender in onlineUsers:
                    """ Visualization for onlineUsers dictionary:
                        onlineUsers["user1"] = <socket for user1 etc etc>
                        onlineUsers["user1"] = <socket for user2 etc etc>
                    """
                    key_for_originUsername = next((key for key, value in onlineUsers.items() if value == originUsername),
                                                  None)  # get the client Handle based on username
                    key_for_sender = next((key for key, value in onlineUsers.items() if value == sender), None)  # get the client Handle based on username

                    if key_for_originUsername not in sessionUsers:
                        sessionUsers.append(onlineUsers[originUsername])  # add recipient to the session
                    if key_for_sender not in sessionUsers:
                        sessionUsers.append(onlineUsers[sender])  # add sender to the server

                    session_key = create_session_key()
                    # get pub key file name
                    pubkeyfile = public_keys[originUsername]

                    # load the pub key
                    pubKey = load_Key(pubkeyfile)

                    # encrypt session key
                    encryptedSession_key = encrypt(session_key, pubKey)

                    # send session key
                    # onlineUsers[originUsername].send(f'{sender}(the sender) and {originUsername}(the recipient) are now in session!'.encode('ascii'))
                    onlineUsers[originUsername].send(f'SESSIONKEY '.encode('ascii'))
                    onlineUsers[originUsername].send(encryptedSession_key)

                    # get pub key file name
                    pubkeyfile = public_keys[sender]

                    # load the pub key
                    pubKey = load_Key(pubkeyfile)

                    # encrypt session key
                    encryptedSession_key = encrypt(session_key, pubKey)

                    # send session key
                    # onlineUsers[sender].send(f'{sender}(the sender) and {originUsername}(the recipient) are now in session!'.encode('ascii'))
                    onlineUsers[sender].send(f'SESSIONKEY '.encode('ascii'))
                    onlineUsers[sender].send(encryptedSession_key)
                else:
                    client.send("Invalid ACCEPT request. One of the parties is not online.".encode('ascii'))
            else:
                broadcast(message, client)

        except:
            if client in sessionUsers:
                index = sessionUsers.index(client)
                sessionUsers.remove(client)
                client.close()
                nickname = nicknames[index]
                broadcast(f'{nickname} left the chat!'.encode('ascii'), None)
                onlineUsers.pop(nickname)
                nicknames.remove(nickname)
            else:
                print("A user has disconnected!")
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

            # sessionUsers.append(client) Don't just add the user to the session. Only add them if INVITE/ACCEPT command is followed through
            # broadcast(f'{nickname} joined the chat!'.encode('ascii'), client)
            client.send('Connected to the server!\n\tIf you would like to invite, type "INVITE"'.encode('ascii'))

            thread = threading.Thread(target=handle, args=(client,))
            thread.start()

        else:
            print(f'{nickname} exists, but the password is incorrect')
            client.send('RESTART'.encode('ascii'))


print("Server is listening..")
receive()
