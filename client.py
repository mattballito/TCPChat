import socket
import threading
import json
import hashlib
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

host = '127.0.0.1'
port = 55555

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

# Generate RSA key pair
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# Get the public key in PEM format
public_key = private_key.public_key()
public_key_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Get the private key in PEM format
private_key_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)


username = input("Enter your username: ")
password = input("Enter your password: ")


def decrypt_with_private_key(ciphertext, priv_key):
    try:
        decrypted_message = priv_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        decrypted_message = decrypted_message.decode('ascii')
    except Exception as e:
        print("Decryption error:", e)
        decrypted_message = None
    return decrypted_message



def receive():
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
                    
                    message = client.recv(1024).decode('ascii')
                    if message == 'REQKEY':
                        client.send(public_key_pem)
                    

            elif message.startswith('INVITATION'):
                inviter = message.split(' ')[1]
                print(f'You have received an invitation from {inviter}!\nType "ACCEPT {inviter}" to accept the invitation.')
            elif message.startswith('CIPHER'):
                encoded_ciphertext = client.recv(1024)
                ciphertext = base64.b64decode(encoded_ciphertext)
                print("Got ciphertext from Server:\n\t", ciphertext)
                decrypted_message = decrypt_with_private_key(ciphertext, private_key)
                print(f'Client has decrypted it as: {decrypted_message}')


            else:
                print(message)

            if message == 'RESTART':
                print("Invalid login. Please restart the client!")
                client.close()

        except Exception as e:
            print("This is error trace:")
            print(e)
            print("An error occurred!")
            client.close()
            break

def write():
    #global private_chat_active, private_chat_partner
    while True:
        message = input()
        if message.startswith('INVITE'):
            # Print the generated keys
            #print("\nPrivate Key:\n", private_key_pem.decode())
            
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
        elif message.startswith('LEAVE'):
            client.send(f'LEAVE'.encode('ascii'))

        

        else:
            client.send(message.encode('ascii'))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()

