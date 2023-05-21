import socket
import threading
import json
import hashlib
import cryptography
from cryptography.fernet import Fernet
import rsa


host = '127.0.0.1'
port = 55555

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

username = input("Enter your username: ")
password = input("Enter your password: ")

private_chat_active = False
session_key= b''

private_keys =  {"user1":"privateKey1.pem" ,
    "user2": "privateKey2.pem",
    "user3": "privateKey3.pem"
}
def load_Key(file):
    with open(file,'rb') as p:
        privateKey = rsa.PrivateKey.load_pkcs1(p.read())
    return privateKey

def decrypt_key(cipher, key):
    print("in decryption section")
    try:
        return rsa.decrypt(ciphertext, key)
    except:
        return False

def receive():
    global private_chat_active, session_key
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

            elif message.startswith('INVITATION'):
                inviter = message.split(' ')[1]
                print(f'You have received an invitation from {inviter}!\nType "ACCEPT {inviter}" to accept the invitation.')
    
            elif message.startswith('SESSIONKEY '):
                print("session key message recieved")
                print(username)
                #open to recieve of session key
                encrypted_session_key = client.recv(1024)
                print(encrypted_session_key)
                privateKeyFile = private_keys[username]
                print(privateKeyFile)
                privatekey= load_Key(privateKeyFile)
                print(privatekey)
                decrypted_sessionKey = rsa.decrypt(encrypted_session_key, privatekey)
                print(decrypted_sessionKey)
                session_key = decrypted_sessionKey
                private_chat_active = True
                print('Invite accepted, session key received')
                print(type(session_key))
            elif message.startswith('CHAT '):
                print("Chat reached")
                if private_chat_active:
                    print("private chat is active")
                    encrypted_message = message.split(' ', 2)[2].encode('ascii')
                    fernet = Fernet(session_key)
                    decrypted_message = fernet.decrypt(encrypted_message).decode('utf-8')
                    print(f'{decrypted_message}')

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
    global private_chat_active, session_key
    while True:
        message = input()
        if message.startswith('INVITE'):
            
            if (len(message.split(' ')) < 2):
                print("Invalid input. Please enter in the followng format:\n\tINVITE <username>")
            else:
                recipient = message.split(' ')[1]
                client.send(f'INVITE {recipient} {username}'.encode('ascii'))
            

        elif message.startswith('ACCEPT'):
            if (len(message.split(' ')) < 2):
                print("Invalid input. Please enter in the followng format:\n\tACCEPT <username>")
            else:
                inviter = message.split(' ')[1]
                client.send(f'ACCEPT {inviter} {username}'.encode('ascii'))
        elif private_chat_active:
            if message.startswith('ENDCHAT'):
                client.send('ENDCHAT'.encode('ascii'))
                private_chat_active = False
    
            elif message:
                fernet = Fernet(session_key)
                encrypted_message = fernet.encrypt(message.encode('utf-8'))  # Encode message to bytes
                client.send(f'CHAT '.encode('ascii') + encrypted_message)
        

        else:
            client.send(message.encode('ascii'))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
