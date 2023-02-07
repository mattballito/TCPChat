import socket
import threading
import json

userName = input("Enter your username: ")
passWord = input("Enter your password: ")
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

def receive():
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(userName.encode('ascii'))
                client.send(passWord.encode('ascii'))
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
            
        except:
            print("An error occured!")
            client.close()
            break



def write():
    while True:
        message = f'{userName}: {input("")}'
        client.send(message.encode('ascii'))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()