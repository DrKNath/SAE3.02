import socket
import threading
import random

class Client:
    def __init__(self,name: str , host: str ='0.0.0.0', port: int = 0):
        self.__name = name
        self.__host = host
        self.__port = port

        self.__list_router = []
        self.__list_client = []
        self.__route = []

        self.__lock = threading.Lock() 
    

    def start(self):

        #thread Master co
        thread_master = threading.Thread(target=self.connection_master)
        thread_master.daemon = True
        thread_master.start()

        #Thread rcv msg 
        thread_rcv = threading.Thread(target=self.receive_msg)
        thread_rcv.daemon = True
        thread_rcv.start()

        #Thread message
        self.send_msg()
        


    def connection(self, host: str, port: int):
        co = socket.socket()
        co.connect((host, port))
        return co
    
    def connection_master(self):
        co_master = self.connection('192.168.1.30',10001)
        co_master.send(f"CLIENT::{self.__name}::{'192.168.1.30'}::{self.__port}".encode('utf-8'))
        try:    
            while True:
            
                data = co_master.recv(1024).decode()
                clients, routers = self.parse_lists(data)

                with self.__lock:
                    self.__list_client = clients
                    self.__list_router = routers
                    
        except:
            co_master.close()
            print("Vous avez été déconnecté du master.")


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
                    "ip": str(ip),
                    "port": int(port),
                    "public_key": pubkey
                })

        return list_clients, list_routers

    def gen_route(self, nb_hop: int = 3):
        with self.__lock:
            routers = list(self.__list_router)

        if not routers:
            print("[ERREUR] Aucun router disponible.")
            return []

        nb_hop = min(nb_hop, len(routers))
        return random.sample(routers, nb_hop)

    def send_msg(self):
        while True:
            message = input(">> ")
            if message == "/quit":
                return
            # Génère une nouvelle route
            self.__route = self.gen_route()
            if not self.__route:
                continue
            print(f"[ROUTE CHOISIE] {self.__route}")
            # Construction du paquet "onion"
            full = f"::{message}"
            route_inverse = self.__route[::-1]  # On commence par l'ultime router
            for router in route_inverse:
                next_ip = router["ip"]
                next_port = router["port"]
                full = f"::{next_ip}::{next_port}{full}"
            print(f"[PAQUET FINAL] {full}")
            # Envoi du message au premier router
            first = self.__route[0]
            try:
                sock = self.connection(first["ip"], first["port"])
                sock.send(full.encode("utf-8"))
                sock.close()
            except:
                print("[ERREUR] Impossible d’envoyer au premier router.")


    def receive_msg(self):
        server = socket.socket()
        server.bind((self.__host, self.__port))
        server.listen(5)

        print(f"[INFO] Client en écoute sur {self.__host}:{self.__port}")

        while True:
            cli, addr = server.accept()
            threading.Thread(target=self.handle_incoming, args=(cli, addr), daemon=True).start()

    def handle_incoming(self, cli, addr):
        try:
            msg = cli.recv(2048).decode()
            print(f"\n[MSG REÇU] {msg}\n>> ", end="")
        except:
            pass
        cli.close()



if __name__ == "__main__":
    name = str(input("name >>"))
    port = int(input("port >>"))
    client_instance = Client(name=name, port=port)
    client_instance.start()
