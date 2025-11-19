import socket
import threading
import re

class router:
    def __init__(self,name: str, host: str = '0.0.0.0', port: int = 0):
        self.__name = name
        self.__host = host
        self.__port = port
        self.__list_connected = []
        self.__router_socket = socket.socket()
        self.__master_address: str = '192.168.1.30'
        self.__master_port:int = 10000

        print(f"Router démarrré sur {self.__host}:{self.__port}")

    def start(self):
        # Socket client pour parler au master
        self.__master_socket = socket.socket()
        self.__master_socket.connect((self.__master_address, self.__master_port))
        self.__master_socket.send(
            f"ROUTER::{self.__name}::{self.__host}::{self.__port}".encode('utf-8')
        )
        print(f"Connecté au master sur {self.__master_address}:{self.__master_port}")

        # Socket serveur pour écouter les clients
        self.__router_socket.bind((self.__host, self.__port))
        self.__router_socket.listen(5)
        print(f"Router en écoute sur {self.__host}:{self.__port}")

        self.new_connection()


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
    port = int(input("Entrez le port du routeur: "))
    router = router(name = 'R1', port = port)
    router.start()
    

