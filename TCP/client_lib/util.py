from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
from threading import Thread
import lib
from lib.lib import *
import globals
from rich.progress import Spinner
import time
from rich.progress import Progress
import hashlib
import os
import sys
import time
import json
from client_lib.connection import *

directory = ''
CHUNK_NUMBER = globals.CHUNK_NUMBER

def merge_file(file_name):
    file_path = os.path.join("download", file_name)
    with open(file_path, 'wb') as f:
        for i in range(CHUNK_NUMBER):
            chunk_path = os.path.join("download", file_name + f".part{i+1}")
            with open(chunk_path, 'rb') as chunk_f:
                f.write(chunk_f.read())
            os.remove(chunk_path)

def download_chunk(file_name, offset, length, chunk_index):
    LOG = lib.LOG
    client = socket(AF_INET, SOCK_STREAM)
    client.connect((globals.SERVER_HOST, globals.SERVER_PORT))
    dc_aes_key = handshake(client)
    client_ip, client_port = client.getsockname()
    payload = {
        'file_name': file_name,
        'offset': offset,
        'length': length,
        'chunk_index': chunk_index
    }
    client.sendall(encrypt_packet(create_packet(json.dumps(payload), client_ip, client_port, 'D', client), dc_aes_key))
    download_path = os.path.join("download", file_name + f".part{chunk_index}")
    # try:
    with open(download_path, 'wb') as f:
    
        client.settimeout(5)
        while True:
            data = client.recv(1024+30)
            if not data:
                raise Exception('There is an error when downloading file')
            data = decrypt_packet(data, dc_aes_key)
            f.write(data)
            client.sendall(encrypt_packet(create_packet("", client_ip, client_port, 'A', client), dc_aes_key))
        return 1
    # except Exception as e:
    #     LOG.error(f"Error: {e}")
    #     return -1

def download_file(c, client_ip, client_port, file_name, aes_key):
    LOG = lib.LOG
    # print('send ', create_packet(file_name, 'D', c))
    payload = {
        'file_name': file_name,
        'chunk_number': CHUNK_NUMBER
    }
    # time.sleep(3)
    c.sendall(encrypt_packet(create_packet(json.dumps(payload), client_ip, client_port, 'E',  c), aes_key))
    # c.send(create_packet(file_name, 'D', c))
    try:
        data = c.recv(1024)
        if not data:
            raise Exception('No data')
        data = decrypt_packet(data, aes_key)
        protocol_name, sender_ip, sender_port, type_request, payload_length, payload = GEYS_parse(data)
        payload = json.loads(payload.decode())
        response = payload['response']
        if response == 'N':
            raise Exception('File not found')
        threads = []
        file_size = payload['file_size']
    
        LOG.info(f"[cyan]Downloading file: [green]{file_name}[/] - {file_size // (2**20)} MB[/cyan]", extra={"markup": True})   
        # LOG.info(f"     File size: {file_size}")
        chunk_size = (file_size + CHUNK_NUMBER - 1) // CHUNK_NUMBER
        for i in range(CHUNK_NUMBER):
            offset = chunk_size * i
            length = min(chunk_size, file_size - offset)
            thr = Thread(target=download_chunk, args=(file_name, offset, length, i+1))
            thr.start()
            threads.append(thr)
            
        for thr in threads:
            thr.join()
        merge_file(file_name)
        return 1
        
        # CHUNK_NUMBER = globals.CHUNK_NUMBER
        # threads = [
        #     Thread(target=download_chunk, args=(file_name, offset, i))
        #     for i in range(CHUNK_NUMBER)
        # ]
        # tasks = [
        #     {"desc": f"Downloading chunk {i+1}", "duration": 1}
        #     for i in range(CHUNK_NUMBER)
        # ]
        # task_ids = [
        #     progress.add_task(task["desc"], total=100) for task in tasks
        # ]
    except Exception as e:
        LOG.error(f"Error: {e}")
        return -1
        
def msg_found_file(files_list):
    if len(files_list) == 0:
        return '[magenta]No file found in your input.txt[/]'
    msg = '[magenta]Found file in your input.txt:[/]\n'
    for i in range(len(files_list)):
        msg = msg + f'{i+1}. [green]{files_list[i]}[/]\n'
    return msg

def getFirstChecking(file_path):
    files_list = []
    with open(file_path, 'r') as f:
        files = f.readlines()
        for file in files:
            file = file.strip()
            files_list.append(file)
    return files_list

def handle_process(c, client_ip, client_port, aes_key):
    LOG = lib.LOG
    CONSOLE = lib.CONSOLE
    # try:
    # while True:
    files_list = []
    with CONSOLE.status("[cyan]First checking your input.txt...") as status:
        spinner = Spinner("circle")
        file_path = os.path.join(directory, 'input.txt')
        # print(file_path)
        sha256 = calculate_hash_sha256(file_path)
        if sha256['code'] == -1:
            with open(file_path, 'w') as f:
                pass
        sha256 = calculate_hash_sha256(file_path)
        files_list = getFirstChecking(file_path)
        time.sleep(2)

    LOG.info(msg_found_file(files_list), extra={"markup": True})

    while True:
        if len(files_list) != 0:
            LOG.info("[cyan]Starting download files...[/]", extra={"markup": True})
        for i in range(len(files_list)):
            file_name = files_list[i] 
            response = download_file(c, client_ip, client_port, file_name, aes_key)
            if response == 1:
                LOG.info(f"[green]Downloaded file {file_name} successfully[/]", extra={"markup": True})
            break
        break
        time.sleep(5)
            
    
        # with CONSOLE.status("[cyan]Scanning changes in your input.txt...") as status:
        #     spinner = Spinner("circle")  # Chọn loại spinner, có thể là "circle", "dots", "star", ...
        #     for _ in range(10):
        #         time.sleep(0.1)
                # spinner.next()
                
            
        
    # except Exception as e:
    #     LOG.error(f"Error: {e}")
        
def getFileList(c, client_ip, client_port, AES_KEY):
    # print('send ', create_packet("", 'F', c))
    c.sendall(encrypt_packet(create_packet("", client_ip, client_port, 'F', c), AES_KEY))
    # c.send(create_packet("", 'F', c))
    data = c.recv(1024)
    if not data:
        return -1
    data = decrypt_packet(data, AES_KEY)
    protocol_name, sender_ip, sender_port, type_request, content_length, payload = GEYS_parse(data)
    # print(protocol_name, sender_ip, sender_port, type_request, content_length, chunk_number, file_name)
    return {
        'protocol_name': protocol_name,
        'sender_ip': sender_ip,
        'sender_port': sender_port,
        'type_request': type_request,
        'content_length': content_length,
        'data': data[15: 15+content_length]
    }
    
    