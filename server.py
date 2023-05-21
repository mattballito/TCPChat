import socket
import threading
import json
import hashlib
from collections import defaultdict

host = "127.0.0.1"
port = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

sessionUsers = []
nicknames = []
pendingRequests = defaultdict(bool) # tracks users that have sent chat requests

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
                originUsername = list_message[2] # this guy is trying to initiate an invite
                pendingRequests[originUsername] = False
                if recipient != originUsername and recipient in onlineUsers: #make sure you aint inviting yourself and the guy is online
                    pendingRequests[originUsername] = True # track his request
                if recipient in onlineUsers:
                    onlineUsers[recipient].send(f'INVITATION {originUsername}'.encode('ascii'))
            elif list_message[0] == 'LEAVE':
                if client in sessionUsers:
                    sessionUsers_copy = sessionUsers[:]  # Create a copy of sessionUsers
                    for c in sessionUsers_copy:
                        if c is client:
                            sessionUsers.remove(c)  # Remove the client using identity comparison
                    client.send("You have been removed from the session!".encode('ascii'))
                else:
                    client.send("You aren't in the session!".encode('ascii'))


            elif list_message[0] == 'ACCEPT':
                sender = list_message[1] # the guy who initiated the request
                originUsername = list_message[2] # the guy who's accepting it

                if sender not in pendingRequests:
                    client.send(f'{sender} has not initiated a request with you!'.encode('ascii'))
                elif originUsername in onlineUsers and sender in onlineUsers and pendingRequests[sender]:
                    """ Visualization for onlineUsers dictionary:
                        onlineUsers["user1"] = <socket for user1 etc etc>
                        onlineUsers["user1"] = <socket for user2 etc etc>
                    """
                    pendingRequests[sender] = False # set their request back to false
                    key_for_originUsername = next((key for key, value in onlineUsers.items() if value == originUsername), None) #get the client Handle based on username
                    key_for_sender = next((key for key, value in onlineUsers.items() if value == sender), None) # get the client Handle based on username

                    # The two for loops here are iterating through a copy of sessionusers. This is necessary because objects are compared by their identity, not their content
                    # the solution is to iterate over a copy of sessionUsers and remove the client using it's identity (reference) rather than relying on == comparison

                    if key_for_originUsername not in sessionUsers:
                        sessionUsers_copy = sessionUsers[:]  # Create a copy of sessionUsers to parse for already existing clients
                        for c in sessionUsers_copy:
                            if c is onlineUsers[originUsername]:
                                break
                        else:
                            sessionUsers.append(onlineUsers[originUsername])  # Add recipient to the session

                    if key_for_sender not in sessionUsers:
                        sessionUsers_copy = sessionUsers[:]  # Create a copy of sessionUsers to parse for already existing clients
                        for c in sessionUsers_copy:
                            if c is onlineUsers[sender]:
                                break  # Break if the client already exists in sessionUsers
                        else:
                            sessionUsers.append(onlineUsers[sender])  # Add sender to the session

                    onlineUsers[originUsername].send(f'{sender}(the sender) and {originUsername}(the recipient) are now in session!\n\tType LEAVE to exit'.encode('ascii'))
                    onlineUsers[sender].send(f'{sender}(the sender) and {originUsername}(the recipient) are now in session!\n\tType LEAVE to exit'.encode('ascii'))
                else:
                    client.send("Invalid ACCEPT request. One of the parties is not online, or they haven't sent you a request.".encode('ascii'))
            else:
                if client in sessionUsers:
                    broadcast(message, client)

        except:
            if (client in sessionUsers):
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

            #sessionUsers.append(client) Don't just add the user to the session. Only add them if INVITE/ACCEPT command is followed through
            #broadcast(f'{nickname} joined the chat!'.encode('ascii'), client)
            client.send('Connected to the server!\n\tIf you would like to invite, type "INVITE"'.encode('ascii'))

            thread = threading.Thread(target=handle, args=(client,))
            thread.start()

        else:
            print(f'{nickname} invalid login!')
            client.send('RESTART'.encode('ascii'))


print("Server is listening..")
receive()
