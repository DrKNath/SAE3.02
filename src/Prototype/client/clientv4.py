import socket
import threading
import random
import time
from crypto import crypto


class Client:
    def __init__(self,name: str , host: str ='0.0.0.0', port: int = 0):
        self.__name = name
        self.__host = host
        self.__port = port

        self.__master_host:str
        self.__master_port:int

        self.__crypto = crypto()

        self.__list_router = []
        self.__list_client = []
        self.__route = []

        self.__lock = threading.Lock()

        self.__desitnation_ip = '192.0.0.2'
        self.__destination_port = 30002
    
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

    def connection_master_loop(self):
        while self.__running:
            try:
                print(f"[INFO] Tentative de connexion au master {self.__master_host}:{self.__master_port}")

                self.__master_socket = self.connection(
                    self.__master_host,
                    self.__master_port
                )

                print("[INFO] Connecté au master")

                self.__master_socket.send(
                    f"CLIENT::{self.__name}::192.0.0.2::{self.__port}".encode("utf-8")
                )

                while self.__running:
                    data = self.__master_socket.recv(1024)

                    if not data:
                        raise ConnectionError("Connexion perdue")

                    clients, routers = self.parse_lists(data.decode())

                    with self.__lock:
                        self.__list_client = clients
                        self.__list_router = routers

            except (ConnectionError, socket.error) as e:
                print(f"[WARN] Master indisponible : {e}")

            finally:
                if self.__master_socket:
                    try:
                        self.__master_socket.close()
                    except:
                        pass
                    self.__master_socket = None

                print("[INFO] Reconnexion dans 3 secondes...")
                time.sleep(3)

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

                e, n = pubkey.split(":")
                pubkey= (int(e), int(n))

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
    
    def build_onion(self, message: str, route, destination_ip, destination_port):
        layer = f"{destination_ip}::{destination_port}::{message}"
        
        for router in reversed(route):
            pubkey = router["public_key"]
            encrypted_layer = self.__crypto.encrypt(layer, pubkey)
            
            # Si ce n'est PAS le premier routeur
            if router != route[0]:
                ip = router["ip"]
                port = router["port"]
                layer = f"{ip}::{port}::{encrypted_layer}"
            else:
                # Pour le premier, pas d'enrobage
                layer = encrypted_layer
        
        return layer
    
    def send_msg(self):
        while True:
            message = input(">> ").strip()
            if message.startswith("/"):
                self.console_msg(message)
            # Génère une nouvelle route
            self.__route = self.gen_route()
            if not self.__route:
                continue
            print(f"[ROUTE CHOISIE] {self.__route}")

            onion = self.build_onion(message, self.__route, self.__desitnation_ip, self.__destination_port)
            first = self.__route[0]

            try:
                print(onion)
                sock = self.connection(first["ip"], first["port"])
                sock.send(onion.encode("utf-8"))
                sock.close()
            except:
                print("[ERREUR] Impossible d’envoyer au premier router.")

    def console_msg(self, msg: str):
        parts = msg.split()
        match parts:
            case ["/ip","master", ip]:
                self.__master_host = ip
                print(f"[INFO] IP master définie à {ip}")
            case ["/port","master", port]:
                self.__master_port = int(port)
                print(f"[INFO] Port master défini à {port}") 
            case _:
                print("[ERREUR] Commande inconnue.")

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
            msg = cli.recv(4096).decode()
            print(f"\n[MSG REÇU] {msg}\n>> ", end="")
        except:
            pass
        cli.close()

if __name__ == "__main__":
    name = str(input("name >>"))
    port = int(input("port >>"))
    client_instance = Client(name=name, port=port)
    client_instance.start()
