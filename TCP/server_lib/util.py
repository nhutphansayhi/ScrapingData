from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from Crypto.Util.number import bytes_to_long, long_to_bytes
from threading import Thread
from lib.lib import *
import os
import lib
import globals
import lib.log
import json
import time


def getFiles(directory):
    files = [
        {'name': f, 'size': os.path.getsize(os.path.join(directory, f))}
        for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))
    ]
    return files

def checkExistFile(file_name):
    return os.path.exists(os.path.join('database', file_name))

def getFileSize(file_name):
    return os.path.getsize(os.path.join('database', file_name))

def handle_client(c, a, AES_KEY):
    LOG = lib.LOG
    HOST = globals.SERVER_HOST
    PORT = globals.SERVER_PORT
    try:
        while True:
                # LOG.info("Finist get files")
            data = c.recv(1024)
            
            # if not data:
            #     break
            packet = decrypt_packet(data, AES_KEY)
            # print('receive ', packet)
            # packet = data
            protocol_name, sender_ip, sender_port, type_request, content_length, payload = GEYS_parse(packet)
            # print(protocol_name, sender_ip, sender_port, type_request, content_length, chunk_number, file_name)
            if type_request == 'F':
                LOG.info(f"[bold green][{protocol_name}][/bold green] Received packet from {int_to_ip(sender_ip)}:{sender_port} [bold magenta]Get files list[/bold magenta]" , extra={"markup": True})
                files_list = json.dumps(getFiles('Database'))
                c.sendall(encrypt_packet(create_packet(files_list, HOST, PORT, 'R', c), AES_KEY))
            elif type_request == 'D':
                payload = json.loads(payload.decode())
                file_name = payload['file_name']
                offset = payload['offset']
                length = payload['length']
                chunk_index = payload['chunk_index']
                LOG.info(f"[bold green][{protocol_name}][/bold green] Received packet from {int_to_ip(sender_ip)}:{sender_port} [bold magenta]Download file:[/bold magenta] [green]{file_name} Part {chunk_index} [/green]" , extra={"markup": True})
                
                file_path = os.path.join('Database', file_name)
                bytes_readed = 0
                # LOG.info(length)
                c.settimeout(5)
                with open(file_path, 'rb') as f:
                    f.seek(offset)
                    while bytes_readed < length:
                        # LOG.info(bytes_readed)
                        data = f.read(min(1024, length - bytes_readed))
                        c.sendall(encrypt_packet(data, AES_KEY))
                        bytes_readed += len(data)
                        ACK = c.recv(1024)
                        
                    
                    # LOG.info("pp")
                
                # c.sendall(encrypt_packet(create_packet('', HOST, PORT, 'S', c), AES_KEY))
                # LOG.info("kkk")
                
            elif type_request == 'E':
                payload = json.loads(payload.decode())
                file_name = payload['file_name']
                chunk_number = payload['chunk_number']
                LOG.info(f"[bold green][{protocol_name}][/bold green] Received packet from {int_to_ip(sender_ip)}:{sender_port} [bold magenta]Download file:[/bold magenta] [green]{file_name}[/green] [bold magenta]| Number of chunk:[/bold magenta] [green]{chunk_number}[/green]" , extra={"markup": True})
                exist_file = checkExistFile(file_name)
                if exist_file:
                    file_size = getFileSize(file_name)
                    res = {
                        'response': 'Y',
                        'file_size': file_size
                    }
                    c.sendall(encrypt_packet(create_packet(json.dumps(res), HOST, PORT, 'R', c), AES_KEY))
                else:
                    res = {
                        'response': 'N'
                    }
                    c.sendall(encrypt_packet(create_packet(json.dumps(res), HOST, PORT, 'R', c), AES_KEY))
            # for chunk_index in range(1, 4):
            #     _c, _a = c.accept()
            # for chunk_index in range(1, 4):
            #     _c, _a = c.accept()
        
    except Exception as e:
        LOG.error(f"Error: {e}")
    finally:
        LOG.info(f"{int_to_ip(sender_ip)}:{sender_port} disconnected")
        c.close()
    
            
     
        
        
def generate_RSA_key():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return public_key, private_key
