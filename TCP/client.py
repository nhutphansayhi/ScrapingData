from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
import asyncio
import os
from client_lib.util import *
from client_lib.connection import *
import sys
import lib
from lib.lib import *
from lib.log import *
import globals

LOG = lib.LOG
    
def main():
    HOST = globals.SERVER_HOST
    PORT = globals.SERVER_PORT
    
    c = socket(AF_INET, SOCK_STREAM)
    try:
        c.connect((HOST, PORT))
        AES_KEY = handshake(c)
        
        encrypted_files = c.recv(1024)
        print(encrypted_files)
        # files = decrypt_packet(encrypted_files, AES_KEY)
        LOG.info("Files in server directory:")
        # LOG.info(files.decode())

        try:
            x = input("Enter file name to download: ")
        except KeyboardInterrupt:
            LOG.info("Client stopped.")
        finally:
            c.close()
    except ConnectionRefusedError:
        LOG.error("Can not connect to server.")
        c.close()        

if __name__ == "__main__":
    main()