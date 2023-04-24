import hashlib

passwords = ['pass1', 'pass2', 'pass3']
passwords[0] = hashlib.sha256(passwords[0].encode()).hexdigest()
passwords[1] = hashlib.sha256(passwords[0].encode()).hexdigest()
passwords[2] = hashlib.sha256(passwords[0].encode()).hexdigest()
print(passwords)


#for password in passwords:
#    hashed_password = hashlib.sha256(password.encode()).hexdigest() 
#    print(hashed_password)