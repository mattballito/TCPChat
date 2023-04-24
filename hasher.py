import hashlib

passwords = ['pass1', 'pass2', 'pass3']
passwords[0] = hashlib.sha256(passwords[0].encode()).hexdigest()
passwords[1] = hashlib.sha256(passwords[1].encode()).hexdigest()
passwords[2] = hashlib.sha256(passwords[2].encode()).hexdigest()
print(passwords)

#We can also take the loop method over here. Do for loop
