# Authors
* Matthew Butner
* Parthiv Desai
* Kim Eaton
* Liam McHugh 
* Alejandro Ramos Jr
* Hemanth Rishi Sivakumar
* Joji Thomas
* Luis Angel Valle-Arellanes

# Contributions
* Matthew Butner: Implementation of base chat application, including the protocols used by the socket. Secure session key distribution, integrated both RSA and DSA to the primary codebase, generated keys dynamically for symmetric keys, RSA, and DSA, managed codebase
* Parthiv Desai
Created hashed passwords for the passwords.Successfully implementing the INVITE and ACCEPT functionality for the chat. Also, added the ENDCHAT functionality for ending the chat. Working on a different initial approach for the TCP chat.Integrating RSA and DSA together.Fixing bugs like user receiving the encrypted message instead of the actual message.
* Kim Eaton: Creation of public/private key files, creation of session key and implementation of secure distribution. Implementation of message encryption/decryption with session key. Documentation(diagrams, descriptions, formatting). RSA signature.(with help)
* Joji Thomas - Implemented connections  for First client will start up and then login. Once the first client logs in they are automatically added to the server's session. They can then invite players but at this point nobody else should be online.
* Liam McHugh: Worked on implementing DSA. Helped debugging.  Also, worked on the documentation.
* Luis Angel Valle-Arellanes: Implementing RSA and DSA, fixing bugs such has implementing module, fixing types, preventing RSA from being decrypted using a public key
* Alejandro Ramos Jr
* Hemanth Rishi Sivakumar



# Installation

```pip install cryptography```


#  To Start Server
```python server.py```


#  To Start Client
```python client.py```

# COMMANDS
After client has logged in, the following commands may be ran:

```ONLINE``` - Shows all the online users

```INVITE <username>``` - Checks if user is online

```ACCEPT <username>``` - Accepts request to join chat session from certain username (if they have sent one)

```LEAVE``` - Leaves the chat session

```DIGSIG``` - Verifies Digital Signature using DSA or RSA

