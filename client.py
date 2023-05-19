import socket
import threading
import json
import hashlib

userName = input("Enter your username: ")
passWord = input("Enter your password: ")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

def receive():
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(userName.encode('ascii'))
                hashed_password = hashlib.sha256(passWord.encode()).hexdigest()
                client.send(hashed_password.encode('ascii'))
            elif message == "USERLIST":
                message = client.recv(1024).decode('ascii')
                if (message == "LISTDATA"):
                    received_data = client.recv(1024)
                    deserialized_data = json.loads(received_data.decode())

                if (len(deserialized_data) > 0):
                    print("Here are the online users:\n", deserialized_data)
                else:
                    print("No other users are online at the moment\n")
            else:
                print(message)
                if message == 'RESTART':
                    print("Invalid login. Please restart the client!")
                    client.close()
        except:
            print("An error occurred!")
            client.close()
            break

def write():
    started_chats = set()
    while True:
        print("Type CHATNOW to initiate a chat session.")
        user_input = input()
        if user_input == "CHATNOW":
            user_to_chat_with = input("Enter the username whom you want to communicate with: ")
            if user_to_chat_with not in started_chats:
                client.send(f"CHATWITH {user_to_chat_with}".encode('ascii'))
                started_chats.add(user_to_chat_with)
        else:
            message = f'{userName}: {user_input}'
            client.send(message.encode('ascii'))



receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
