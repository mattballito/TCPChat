
import rsa 

(publicKey, privateKey) = rsa.newkeys(1024)
with open('publicKey1.pem', 'wb') as p:
    p.write(publicKey.save_pkcs1('PEM'))
with open('privateKey1.pem', 'wb') as p:
    p.write(privateKey.save_pkcs1('PEM'))