import configparser



def get_config():
    global SERVER_HOST, SERVER_PORT, SERVER_BUFSIZ
    config = configparser.ConfigParser()
    config.read('../config.ini')
    SERVER_HOST = config['SERVER']['HOST']
    SERVER_PORT = int(config['SERVER']['PORT'])
    SERVER_BUFSIZ = int(config['SERVER']['BUFSIZ'])
    # print(SERVER_HOST, SERVER_PORT, SERVER_BUFSIZ)
    return SERVER_HOST, SERVER_PORT, SERVER_BUFSIZ