import socket
import threading
import json
import hashlib
from collections import defaultdict
import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa, utils, dsa
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet



host = "127.0.0.1"
port = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

sessionUsers = []
nicknames = []
pendingRequests = defaultdict(bool) # tracks users that have sent chat requests
public_keys_pem = defaultdict(bool)
dsa_keys = defaultdict(bool)


def read_user_registry(file_path):
    user_registry = {}
    with open(file_path, 'r') as file:
        for line in file:
            user, hashed_password = line.strip().split(':')
            user_registry[user] = hashed_password
    return user_registry

userRegistry = read_user_registry('hashed_passwords.txt')
onlineUsers = {}

def get_username_of_client(client_identity):
    for username, value in onlineUsers.items():
        if value is client_identity:
            return username
    return None  # Return None if no match is found

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

def encrypt_with_public_key(message, pub_key):
    # Convert the received public key string to bytes
    received_public_key_bytes = pub_key.encode('ascii')
    byte_message = message
    try:
        public_key = serialization.load_pem_public_key(received_public_key_bytes, backend=default_backend())
        # Encrypt the message
        encrypted_message = public_key.encrypt(
            byte_message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    except Exception as e:
        print(e)
    return encrypted_message

def verify_signature(signature, message, public_key): # RSA
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception as e:
        print("Signature verification failed:", e)
        return False

def generate_symmetric_key():
    # Generate a random key
    key = Fernet.generate_key()
    return key

def encrypt_with_fernet(key, plaintext):
    # Create a Fernet cipher with the key
    cipher = Fernet(key)

    # Encrypt the plaintext
    ciphertext = cipher.encrypt(plaintext)
    return ciphertext

def decrypt_with_fernet(key, ciphertext):
    # Create a Fernet cipher with the key
    cipher = Fernet(key)

    # Decrypt the ciphertext
    plaintext = cipher.decrypt(ciphertext)
    return plaintext


session_key = None
sessionKeyNotActive = True

def handle(client):
    
    while True:
        try:
            message = client.recv(1024)
            string_message = message.decode()
            list_message = string_message.split()
            

            if list_message[0] == 'ONLINE':
                online_list = get_online_users(client)
                client.send(online_list)
            elif list_message[0] == 'DIGSIG(R)':
                signedmsg = client.recv(1024)
                #print(signedmsg)
                try:
                    received_public_key = serialization.load_pem_public_key(
                        public_keys_pem[get_username_of_client(client)].encode('ascii'),
                        backend=default_backend()
                    )
                    received_public_key.verify(
                        signedmsg,
                        'DIGSIG(R)'.encode('ascii'),
                        padding.PSS(
                            mgf=padding.MGF1(hashes.SHA256()),
                            salt_length=padding.PSS.MAX_LENGTH
                        ),
                        hashes.SHA256()
                    )
                    print("Signature is valid.")
                    client.send("RSA Signature is valid!".encode('ascii'))
                except Exception as e:
                    print("Signature is invalid! ", e)
                    client.send("Signature not valid".encode('ascii'))
                
            elif list_message[0] == 'DIGSIG(D)':
                try:
                    signedmsg = client.recv(1024)
                    
                    dsa_key_to_use = serialization.load_pem_public_key( #convert back to key object
                        dsa_keys[get_username_of_client(client)].encode('ascii'),
                        backend=default_backend()
                    )

                    dsa_key_to_use.verify(
                        signedmsg,
                        'DIGSIG(D)'.encode('ascii'),
                        hashes.SHA256()
                    )
                    client.send("DSA Signature is valid!".encode('ascii'))
                except Exception as e:
                    print("Sig not valid..", e)
                    client.send("Signature not valid".encode('ascii'))

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
                    client.send("Removed from session!".encode('ascii'))
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
                    
                        
                        global session_key
                        global sessionKeyNotActive
                        
                        if (sessionKeyNotActive):
                            session_key = generate_symmetric_key()
                            sessionKeyNotActive = False
                        
                       
                        ''' symmetric key encryption steps are below:'''
                        #try:
                            #session_key = generate_symmetric_key()
                            #testText = "haayguys".encode('ascii')
                            #print(testText)
                            #print("Your key: ", session_key)
                            #Ci = encrypt_with_fernet(session_key,testText)
                            #print(Ci)
                            #Pi = decrypt_with_fernet(session_key,Ci)
                            #print("This is your plain: ", Pi)
                        #except Exception as e:
                            #print(e)

                        #print("SERVER, your key: ", session_key)
                        #print(type(session_key))

                        try:
                        
                            ciphertext = encrypt_with_public_key(session_key,public_keys_pem[originUsername]) # CREATE ciphertext for the guy accepting the request
                            onlineUsers[originUsername].send('CIPHER'.encode('ascii'))
                            encoded_ciphertext = base64.b64encode(ciphertext)
                            onlineUsers[originUsername].send(encoded_ciphertext) # send it to him

                            ciphertext = encrypt_with_public_key(session_key,public_keys_pem[sender]) # CREATE ciphertext for the guy initiating the request
                            onlineUsers[sender].send('CIPHER'.encode('ascii'))
                            encoded_ciphertext = base64.b64encode(ciphertext)
                            onlineUsers[sender].send(encoded_ciphertext) #send it to him
                        except Exception as e:
                            print("the error happens here!!!!!!", e)

                    
                else:
                    client.send("Invalid ACCEPT request. One of the parties is not online, or they haven't sent you a request.".encode('ascii'))
            else:
                if client in sessionUsers:
                    broadcast(message, client)

        except:
            if (client in sessionUsers):

                for user in sessionUsers.copy(): #remove from session
                    if user == client:
                        sessionUsers.remove(user)
                        break

                nickname = get_username_of_client(client)
                print("The nickname is...",nickname)
                #for username, value in public_keys.items():
                    #print(f'FIRST is the key:{username} and it value is:{value}\n')
                public_keys_pem.pop(nickname)
                broadcast(f'{nickname} left the chat!'.encode('ascii'), None)
                onlineUsers.pop(nickname)
                nicknames.remove(nickname)
                client.close()

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

            client.send('REQKEY'.encode('ascii'))
            client_pub_pem = client.recv(1024).decode('ascii') # for key distro and RSA sig verify
            dsa_pub = client.recv(1024).decode('ascii') # for key distro

            number = "".join(filter(str.isdigit, nickname)) # 1, 2 , or 3
            print(f'Storing user{number} public key')
            
            public_keys_pem[nickname] = client_pub_pem
            dsa_keys[nickname] = dsa_pub

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
