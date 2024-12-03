from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
from threading import Thread

def handshake(c):
    PUBLIC_KEY = c.recv(450)
    cipher_rsa = PKCS1_OAEP.new(RSA.import_key(PUBLIC_KEY))

    # Tạo khóa AES và mã hóa bằng khóa công khai RSA của server
    AES_KEY = get_random_bytes(16)
    encrypted_aes_key = cipher_rsa.encrypt(AES_KEY)
    c.sendall(encrypted_aes_key)
    return AES_KEY