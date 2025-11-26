import socket
import threading
import re
import random

class Client:
    def __init__(self,name: str , host: str ='0.0.0.0', port: int = 0):
        self.__name = name
        self.__host = host
        self.__port = port
        self.__list_router = []
        self.__list_client = []
        self.__route = []


    def start(self):
        
        #Thread connection master
        thread_master = threading.Thread(target=self.connection_master)
        thread_master.daemon = True
        thread_master.start()

        #Thread send msg 
        thread_send = threading.Thread(target=self.send_msg)
        thread_send.daemon = True
        thread_send.start()

        self.receive_msg()
    

    def connection(self, host: str, port: int):
        co = socket.socket()
        co.connect((host, port))
        return co


    def connection_master(self):
        co_master = self.connection('192.168.1.30',10000)
        co_master.send(f"CLIENT::{self.__name}::{self.__host}::{self.__port}".encode('utf-8'))
        while True:
            try: 
                reply = co_master.recv(1024).decode('utf-8')
                if not reply:
                    break
                self.decompilation_msg_master(reply)
            except:
                print("Vous avez été déconnecté du master.")
                break
    

    def decompilation_msg_master(self, msg): 
        pattern =  r'^(CLIENT|ROUTER)\s+(\S+)\s+((?:\d{1,3}\.){3}\d{1,3})\s+(\d+)(?:\s+(\S+))?$'
        match = re.match(pattern, msg)
        if match:
            if match.group(1) == 'CLIENT':
                self.__list_client.append({
                    'name': match.group(2),
                    'ip': match.group(3),
                    'port': int(match.group(4))
                })
            elif match.group(1) == 'ROUTER':
                self.__list_router.append({
                    'name': match.group(2),
                    'ip': match.group(3),
                    'port': int(match.group(4)),
                    'public_key': match.group(5)
                })


    def gen_route(self, nb_hop: int = 3):
        nb_hop = min(nb_hop, len(self.__list_router))
        return random.sample(self.__list_router, nb_hop)
    

    def send_msg(self):
        self.__route = self.gen_route()
        send_socket = self.connection(self.__route[0]['ip'], self.__route[0]['port'])
        while True:
            try:
                message = str(input(">> "))
                if message == '/quit':
                    break
                message =f"::{message}"
                route_inverse = self.__route[::-1]
                for route in range(len(route_inverse)-1):
                    next_ip = route['ip']
                    next_port = route['port']
                    message = f"::{next_ip}::{next_port}{message}"
                send_socket.send(message.encode('utf-8'))
            except:
                print("Impossible d'envoyer le message. Vous êtes peut-être déconnecté.")
                break
        self.__socket.close()
    

    def receive_msg(self):
        recv_socket = socket.socket()
        recv_socket.bind(('0.0.0.0',10002))
        recv_socket.listen(5)
        while True: 
            conn,address = recv_socket.accept()
            try :
                reply = conn.recv(1024).decode()
                if not reply:
                    break
                print(f"\nMessage reçu: {reply}\n>> ", end='')
            except:
                print("Vous avez été déconnecté du serveur.")
                break
    

if __name__ == "__main__":
    host = '0.0.0.0'
    port = 10002
    client = Client(host, port)
    client.start()
