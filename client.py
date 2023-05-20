import socket
import threading
import json
import hashlib

userName = input("Enter your username: ")
passWord = input("Enter your password: ")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

private_chat_active = False
private_chat_partner = ''

def receive():
    global private_chat_active
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(userName.encode('ascii'))
                hashed_password = hashlib.sha256(passWord.encode()).hexdigest()
                client.send(hashed_password.encode('ascii'))
            elif message == "USERLIST":
                message = client.recv(1024).decode('ascii')
                if message == "LISTDATA":
                    received_data = client.recv(1024)
                    deserialized_data = json.loads(received_data.decode())

                    if len(deserialized_data) > 0:
                        print("Here are the online users:\n", deserialized_data)
                    else:
                        print("No other users are online at the moment\n")
            elif message.startswith('INVITE '):
                inviter = message.split(' ')[1]
                print(f'You have received an invitation from {inviter}!\nType "ACCEPT {inviter}" to accept the invitation.')
            elif message.startswith('ACCEPTED '):
                recipient = message.split(' ')[1]
                print(f'Your invitation to {recipient} has been accepted. You can now start a private chat session.')
                private_chat_partner = recipient
                private_chat_active = True
            elif message.startswith('CHAT '):
                sender = message.split(' ')[1]
                chat_message = message.split(' ', 2)[2]
                print(f'{sender}: {chat_message}')
            elif message == 'CHATSTART':
                print("Private chat started. You can now communicate privately.\n")
                private_chat_active = True
            elif message == 'CHATEND':
                print("Private chat ended. You can now communicate publicly.\n")
                private_chat_active = False
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
    global private_chat_partner
    while True:
        message = input("")
        if message.startswith('ENDCHAT'):
            client.send('ENDCHAT'.encode('ascii'))
            private_chat_partner = ''
        elif private_chat_active and private_chat_partner and message:
            client.send(f'CHAT {private_chat_partner} {message}'.encode('ascii'))
        elif message:
            client.send(f'{userName}: {message}'.encode('ascii'))
        else:
            print("Invalid command or message. Please try again.\n")

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
