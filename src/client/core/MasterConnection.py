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
            s.connect(("8.8.8.8", 80))  
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            print("Unable to get Hostname and IP")

    def connect_master(self):
        while self.running and self.core.running:
            try:
                self.sock = socket.socket()
                self.sock.settimeout(2.0)
                self.sock.connect((self.master_host, self.master_port))
                self.sock.settimeout(None)

                self.sock.send(f"CLIENT::{self.core.name}::{self.get_Host_IP()}::{self.core.port}".encode())

                while self.running and self.core.running:
                    data = self.sock.recv(1024)
                    if not data:
                        raise ConnectionError("Connexion perdue")
                    if data and data.decode() == "SHUTDOWN":
                        self.running = False
                        self.core.stop() 
                        return
                    if not data or data.decode() == "STOP":
                        break  


                    if data:
                        clients, routers = self.parse_lists(data.decode())
                        with self.core.lock:
                            self.core.list_clients = clients
                            self.core.list_routers = routers


            except:
                if self.core.running and self.running:
                    print("[WARN] Master indisponible (Tentative...)")
                else:
                    return
            finally:
                if self.sock:
                    try:
                        self.sock.close()
                    except:
                        pass
                    self.sock = None
                if not self.core.running or not self.running:
                    return

                time.sleep(3)
    def parse_lists(self, msg):
        if "||" not in msg: return [], []
        clients_part, routers_part = msg.split("||")
        clients_raw = clients_part.replace("CLIENTS:", "")
        routers_raw = routers_part.replace("ROUTERS:", "")
        list_clients = []
        list_routers = []
        if clients_raw.strip():
            for entry in clients_raw.split(";;"):
                if "::" in entry:
                    name, ip, port = entry.split("::")
                    list_clients.append({"name": name, "ip": ip, "port": int(port)})
        if routers_raw.strip():
            for entry in routers_raw.split(";;"):
                if "::" in entry:
                    name, ip, port, pubkey = entry.split("::")
                    e, n = pubkey.split(":")
                    list_routers.append(
                        {"name": name, "ip": str(ip), "port": int(port), "public_key": (int(e), int(n))})
        return list_clients, list_routers
