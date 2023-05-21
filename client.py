import socket
import threading
import json
import hashlib
import cryptography
from cryptography.fernet import Fernet
import rsa
import random


host = '127.0.0.1'
port = 55555

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

username = input("Enter your username: ")
password = input("Enter your password: ")
print("Would you like to use RSA or Digital Signature Algorithm?")

signatureAlgorithm = input("Enter either 'RSA' or 'DSA': ")
    
private_chat_active = False
session_key= b''
private_chat_partner =""
p = 283
q = 47
g = 60

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

def read_user_DSA_key(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            user, DSAKey = line.strip().split(':')
            if(user == username):
                return DSAKey
    return None

def read_user_DSA_Pubkey(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            user, DSAKey = line.strip().split(':')
            if(user == private_chat_partner):
                return DSAKey
    return None

def DSASignatureGeneration(p, q, g, privKey, M):
    while (True):
        k = random.randint(0, p)
        x = (g ** k) % p
        r = x % q
        if (r == 0):
            continue
        h = hashlib.sha256(M.encode('ascii'))
        h = int(h.hexdigest(), 16)
        i = pow(k, -1, q)
        s = i * (h + privKey * r) % 47
        if (s == 0):
            continue
        return (r, s)


def DSASignatureVerification(p, q, g, pubKey, M, r, s):
    if r > 0 and r < q and s > 0 and s < q:
        w = pow(s, -1, q)
        h = hashlib.sha256(M.encode('ascii'))
        h = int(h.hexdigest(), 16)
        x = ((pow(g, (h * w) % q, p)) * pow(pubKey, (r * w) % q, p)) % p
        v = x % q
        if (v == r):
            return True
    return False

def receive():
    global private_chat_active, session_key, private_chat_partner
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
                #set private chat partner, for nice display of messages
                private_chat_partner = inviter
                print(f'You have received an invitation from {inviter}!\nType "ACCEPT {inviter}" to accept the invitation.')
                print("invitation private chat partner:", private_chat_partner)
    
            elif message.startswith('SESSIONKEY '):
                
                #open to recieve of session key
                encrypted_session_key = client.recv(1024)
                #get private key file
                privateKeyFile = private_keys[username]
                #load private key
                privatekey= load_Key(privateKeyFile)
                #decrypt session key
                decrypted_sessionKey = rsa.decrypt(encrypted_session_key, privatekey)
                #save session key
                session_key = decrypted_sessionKey
                #set chat as active
                private_chat_active = True
                print('Invite accepted, session key received')
            elif message.startswith('CHAT '):
                
                if private_chat_active:
                    #check which algortthm is used for signature
                    #decrypt message
                    #split message into message and sig
                    # validate signature
                    #display message
                    
            
                    encrypted_message = message.split('CHAT ')[1].encode('ascii')
                    fernet = Fernet(session_key)
                    decrypted_message = fernet.decrypt(encrypted_message).decode('utf-8')
                    if(signatureAlgorithm == 'DSA'):
                        result = decrypted_message.split("digSig", 1)
                        decrypted_message = result[0]
                        digSig = result[1]
                        pubKey = int(read_user_DSA_Pubkey("DSA_PublicKeys.txt"))
                        digSig = digSig.replace("(", " ")
                        digSig = digSig.replace(")", " ")
                        digSig = digSig.replace(",", " ")
                        sigValues = digSig.split(" ")
                        r = int(sigValues[1])
                        s = int(sigValues[3])
                        if DSASignatureVerification(p, q, g, pubKey, decrypted_message, r, s):
                            print(f'{private_chat_partner}: {decrypted_message}')
                        else:
                            print("This is not verified")
                    else:
                        print(f'{private_chat_partner}: {decrypted_message}')

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
    global private_chat_active, session_key, private_chat_partner
    while True:
        message = input()
        if message.startswith('INVITE'):
            
            if (len(message.split(' ')) < 2):
                print("Invalid input. Please enter in the followng format:\n\tINVITE <username>")
            else:
                recipient = message.split(' ')[1]
                private_chat_partner = recipient
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
                private_chat_partner= ""
            elif message:
                #suggested message organization: [CHAT + " " + ALGORITHM TYPE + " " + ENCRYPTED MESSAGE
                # Encrypted message = message + " " + signature
                if signatureAlgorithm == 'DSA':
                    #do ds Encryption
                    #build message
                    privKey = int(read_user_DSA_key("DSA.txt"))
                    digSig = str(DSASignatureGeneration(p, q, g, privKey, message))
                    message = message + "digSig" + digSig
                elif signatureAlgorithm == 'RSA':
                    #do rsa ds
                    #build message
                    pass
                fernet = Fernet(session_key)
                encrypted_message = fernet.encrypt(message.encode('utf-8'))  # Encode message to bytes
                client.send(f'CHAT '.encode('ascii') + encrypted_message)
        

        else:
            client.send(message.encode('ascii'))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
