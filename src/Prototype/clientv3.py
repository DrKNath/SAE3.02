import socket
import threading


class Client:
    def __init__(self,name: str , host: str ='0.0.0.0', port: int = 0):
        self.__name = name
        self.__host = host
        self.__port = port
        self.__list_router = []
        self.__list_client = []
        self.__route = []
    

    def start(self):
        self.connection_master()


    def connection(self, host: str, port: int):
        co = socket.socket()
        co.connect((host, port))
        return co
    
    def connection_master(self):
        co_master = self.connection('192.168.1.30',10001)
        co_master.send(f"CLIENT::{self.__name}::{self.__host}::{self.__port}".encode('utf-8'))
        try:    
            while True:
            
                data = co_master.recv(1024).decode()
                print(data)
                print("\n \n \n")
                self.__list_client, self.__list_router = self.parse_lists(data)
                print(self.__list_client)
                print(self.__list_router)
                print("\n \n \n")
        except:
            co_master.close()
            print("Vous avez été déconnecté du master.")


    def recv_long(self, sock):
        full_data = ""

        while True:
            print("a")
            part = sock.recv(1024).decode()
            print("b")
            if part == "__END__":
                break
            full_data += part

        return full_data


    def parse_lists(self, msg):
        clients_part, routers_part = msg.split("||")

        # Enlever les préfixes
        clients_raw = clients_part.replace("CLIENTS:", "")
        routers_raw = routers_part.replace("ROUTERS:", "")

        list_clients = []
        list_routers = []

        # Partie clients
        if clients_raw.strip():  # si non vide
            for entry in clients_raw.split(";;"):
                name, ip, port = entry.split("::")
                list_clients.append({
                    "name": name,
                    "ip": ip,
                    "port": int(port)
                })

        # Partie routers
        if routers_raw.strip():
            for entry in routers_raw.split(";;"):
                name, ip, port, pubkey = entry.split("::")
                list_routers.append({
                    "name": name,
                    "ip": ip,
                    "port": int(port),
                    "public_key": pubkey
                })

        return list_clients, list_routers


if __name__ == "__main__":
    name = str(input("name >>"))
    port = int(input("port >>"))
    client_instance = Client(name=name, port=port)
    client_instance.start()
