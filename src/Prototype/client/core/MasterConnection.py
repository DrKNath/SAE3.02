import time
import socket

class MasterConnection:
    def __init__(self, core):
        self.core = core
        self.master_host = None
        self.master_port = None
        self.sock = None
        self.running = True

    def stop(self):
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
    def get_Host_IP(self): 
        try: 
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # Pas de connexion réelle
            ip = s.getsockname()[0]
            s.close()
            return ip
        except: 
            print("Unable to get Hostname and IP") 

    def connect_master(self):
        while self.running:
            if not self.master_host or not self.master_port:
                time.sleep(1)
                continue
            try:
                print(f"[INFO] Tentative de connexion au master {self.master_host}:{self.master_port}")
                self.sock = socket.socket()
                self.sock.connect((self.master_host, self.master_port))
                print("[INFO] Connecté au master")
                self.sock.send(f"CLIENT::{self.core.name}:{self.get_Host_name_IP}::{self.core.port}".encode())
                
                while self.running:
                    data = self.sock.recv(1024)
                    if not data:
                        raise ConnectionError("Connexion perdue")
                    if data:
                        clients, routers = self.parse_lists(data.decode())
                        with self.core.lock:
                            self.core.list_clients = clients
                            self.core.list_routers = routers

            except (ConnectionError, socket.error) as e:
                print(f"[WARN] Master indisponible : {e}")
            finally:
                if self.sock:
                    try:
                        self.sock.close()
                    except:
                        pass
                    self.sock = None
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
