import socket
import threading

class router:
    def __init__(self, name: str, host: str = '0.0.0.0', port: int = 0):
        self.__name = name
        self.__host = host
        self.__port = port
        self.__public_key = None
        self.__prv_key = None
        self.__list_connected = []
    
    def start(self):
        self.connection_master()

    def connection(self, host: str, port: int):
        co = socket.socket()
        co.connect((host, port))
        return co
    
    def connection_master(self):
        co_master = self.connection('192.168.1.30',10001)
        co_master.send(f"ROUTER::{self.__name}::{self.__host}::{self.__port}::{self.__public_key}".encode('utf-8'))
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

if __name__ == "__main__":
    name = str(input("name >>"))
    port = int(input("port >>"))
    router_instance = router(name=name, port=port)
    router_instance.start()

