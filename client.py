import socket
import threading
import json
import hashlib
import cryptography
from cryptography.fernet import Fernet

host = '127.0.0.1'
port = 55555

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

username = input("Enter your username: ")
password = input("Enter your password: ")

private_chat_active = False
private_chat_partner = ''
session_key=""

def receive():
    global private_chat_active, private_chat_partner, session_key
    while True:
        try:
            message = client.recv(1024).decode('ascii')

            if message == 'NICK':
                client.send(username.encode('ascii'))
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                client.send(hashed_password.encode('ascii'))

            elif message == 'USERLIST':
                message = client.recv(1024).decode('ascii')
                if message == 'LISTDATA':
                    received_data = client.recv(1024)
                    deserialized_data = json.loads(received_data.decode())

                    if len(deserialized_data) > 0:
                        print("Here are the online users:\n", deserialized_data)
                    else:
                        print("No other users are online at the moment.\n")

            elif message.startswith('INVITE '):
                inviter = message.split(' ')[1]
                print(f'You have received an invitation from {inviter}!\nType "ACCEPT {inviter}" to accept the invitation.')

            elif message.startswith('SESSIONKEY '):
                session_key = client.recv(1024)
                print(type(session_key))
                private_chat_active = True
                print('Invite accepted, session key received', session_key)

            elif message.startswith('CHAT '):
                if private_chat_active:
                    encrypted_message = message.split(' ', 2)[2].encode('ascii')
                    fernet = Fernet(session_key)
                    decrypted_message = fernet.decrypt(encrypted_message).decode('utf-8')
                    print(f'{decrypted_message}')

            elif message == 'CHATEND':
                print("Private chat ended. You can now communicate publicly.")
                private_chat_active = False
                private_chat_partner = ''

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
    global private_chat_active, private_chat_partner, session_key
    while True:
        message = input()
        if message.startswith('INVITE'):
            recipient = message.split(' ')[1]
            client.send(f'INVITE {recipient}'.encode('ascii'))

        elif message.startswith('ACCEPT'):
            inviter = message.split(' ')[1]
            client.send(f'ACCEPT {inviter}'.encode('ascii'))

        elif private_chat_active:
            if message.startswith('ENDCHAT'):
                client.send('ENDCHAT'.encode('ascii'))
                private_chat_active = False
                private_chat_partner = ''
            elif message:
                fernet = Fernet(session_key)
                encrypted_message = fernet.encrypt(message.encode('utf-8'))  # Encode message to bytes
                client.send(f'CHAT {private_chat_partner} '.encode('ascii') + encrypted_message)


        else:
            client.send(message.encode('ascii'))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
