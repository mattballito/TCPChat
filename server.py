import socket
import threading
import json

host = "127.0.0.1"
port = 55555


server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((host,port))
server.listen()


sessionUsers = []
nicknames = []

userRegistry = {"user1":"pass1",
				"user2":"pass2",
				"user3":"pass3"}

onlineUsers = {}

def broadcast(message):
	for client in sessionUsers:
		client.send(message)

def handle(client):
	while True:
		try:
			message = client.recv(1024)
			broadcast(message)
		except:
			#terminate this loop
			index = sessionUsers.index(client)
			sessionUsers.remove(client)
			client.close()
			nickname = nicknames[index]
			broadcast(f'{nickname} left the chat!'.encode('ascii'))
			onlineUsers.pop(nickname)
			nicknames.remove(nickname)
			break






def receive():
	while True:
		client, address = server.accept() #accept clients all the time
		print(f"Connected with {str(address)}")	#when a client connects say their address

		client.send('NICK'.encode('ascii'))	#then send to the client the prompt NICK to send nickname
		nickname = client.recv(1024).decode('ascii')	#then recieve the username from client
		password = client.recv(1024).decode('ascii')	#then recieve the password from client
		#print(f'Server read in new password:{password}')

		if (str(nickname) in userRegistry):
			if (userRegistry[f'{nickname}'] == password):
				print(f'{nickname} is now online in the server!')
				onlineUsers[nickname] = client # set table with key as username, value as client variable
				print("SERVER: this is dict:",onlineUsers)
				nicknames.append(nickname)

				
				client.send('USERLIST'.encode('ascii'))	#then prompt the client to enter a list of users to chat with
				client.send('LISTDATA'.encode('ascii'))
				
				

				sendList = [x for x in nicknames if x != nickname]  # use list comprehension to create a new list without the element
				serialized_list = json.dumps(sendList).encode()
				print("SERVER: about to send this list: ", serialized_list)
				
				client.send(serialized_list)

						
				sessionUsers.append(client)
				broadcast(f'{nickname} joined the chat!'.encode('ascii'))
				client.send('Connected to the server!'.encode('ascii'))
				thread = threading.Thread(target=handle, args=(client,))
				thread.start()
			else:
				print(f'{nickname} exists, but password is incorrect')
		else:
			print("No such user exists in registry.")

		

		
		
		

		

print("Server is listening..")
receive()

