from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from threading import Thread
import os
import lib

def getFiles(directory):
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    return files

def handle_client(c, a, AES_KEY):
    LOG = lib.LOG
    LOG.info("Connection from: ", a)
    
   
    fileList = getFiles('Database')
    fileList = '\n'.join(fileList)
    fileList = fileList.encode()
    print(fileList)
    # cipher_aes = AES.new(AES_KEY, AES.MODE_EAX)
    # nonce = cipher_aes.nonce
    # ciphertext, tag = cipher_aes.encrypt_and_digest(pad(fileList, AES.block_size))
    # c.send(nonce + ciphertext)
    
    
    # while True:
    #     # Nhận dữ liệu đã mã hóa từ client
    #     encrypted_data = c.recv(1024)
    #     if not encrypted_data:
    #         break
        
    #     # Giải mã dữ liệu bằng AES
    #     nonce = encrypted_data[:16]
    #     ciphertext = encrypted_data[16:]
    #     cipher_aes = AES.new(aes_key, AES.MODE_EAX, nonce=nonce)
    #     data = cipher_aes.decrypt(ciphertext)
    #     print("Decrypted data:", data.decode())
        
    #     # Nhập phản hồi và mã hóa bằng AES
    #     response = input("Enter response: ")
    #     cipher_aes = AES.new(aes_key, AES.MODE_EAX)
    #     encrypted_response = cipher_aes.nonce + cipher_aes.encrypt(response.encode())
    #     c.send(encrypted_response)
        
        
def generate_RSA_key():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return public_key, private_key
