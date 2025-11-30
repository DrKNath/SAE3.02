import socket
import threading
import re

class router:
    def __init__(self, name: str, host: str = '0.0.0.0', port: int = 0):
        self.__name = name
        self.__host = host
        self.__port = port
        self.__public_key = None
        self.__prv_key = None
        self.__router_socket = socket.socket()

        self.__list_connected = []

    
    def start(self):
        #thread Master co
        thread_master = threading.Thread(target=self.connection_master)
        thread_master.daemon = True
        thread_master.start()

        # Socket serveur pour écouter les clients
        self.__router_socket.bind((self.__host, self.__port))
        self.__router_socket.listen(5)

        self.new_connection()

    def connection(self, host: str, port: int):
        co = socket.socket()
        co.connect((host, port))
        return co
    
    def connection_master(self):
        co_master = self.connection('192.168.1.30',10001)
        co_master.send(f"ROUTER::{self.__name}::{'192.168.1.30'}::{self.__port}::{self.__public_key}".encode('utf-8'))
        # boucle infinie pour maintenir le socket ouvert
        try:
            while True:
                # ici tu peux écouter des messages du master si besoin
                data = co_master.recv(1024)
                if not data:
                    break  # master a fermé la connexion
        except:
            pass
        finally:

            co_master.close()
    
    def new_connection(self):
        while True:
            conn,address = self.__router_socket.accept()
            self.__list_connected.append((conn))

            thread_client = threading.Thread(target=self.routage, args=(conn,))
            thread_client.daemon = True
            thread_client.start()

    def routage(self, conn):
        while True:
            message = conn.recv(1024).decode('utf-8')
            if not message:
                break
            print(message)
            next_ip, next_port, rest = self.decrypt_message(message)
            print(f"{next_ip}:{next_port}")
            if next_ip and next_port:
                forward_socket = socket.socket()
                forward_socket.connect((next_ip, next_port))
                forward_socket.send(rest.encode('utf-8'))
                forward_socket.close()


    def decrypt_message(self, message: str):
        pattern = r'^::([^:]+)::([^:]+)::(.*)$'
        match = re.match(pattern, message)

        if match:
            next_ip = str(match.group(1))
            next_port = int(match.group(2))
            rest = f"::{match.group(3)}"
            
            return next_ip, next_port, rest
        else:
            return None, None, message
    

if __name__ == "__main__":
    name = str(input("name >>"))
    port = int(input("port >>"))
    router_instance = router(name=name, port=port)
    router_instance.start()

