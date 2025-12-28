import socket
import threading
import time
import sys
from crypto.crypto import crypto
import random 

class router:
    def __init__(self, name: str, host: str = '0.0.0.0', port: int = 0):

        key_size = int(sys.argv[1] if len(sys.argv) > 1 else 8)

        self.__name = name
        self.__host = host
        self.__port = port

        self.__master_host:str = None
        self.__master_port:int = None

        self.__crypto = crypto(key_size)
        self.__public_key = self.__crypto.public
        self.__prv_key = self.__crypto.prive

        self.__router_socket = socket.socket()
        self.__list_connected = []

        self.__chunk_buffer = {}
        

    
    def get_Host_IP(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            print("Unable to get Hostname and IP")

    def start(self):
        try:
            self.__router_socket.bind((self.__host, self.__port))
            self.__router_socket.listen(5)
        except:
            print("Port déjà utilisé")
            sys.exit(0)
        #Thread Terminal
        thread_terminal = threading.Thread(target=self.terminal_loop)
        thread_terminal.daemon = True
        thread_terminal.start()

        # Thread Master co
        thread_master = threading.Thread(target=self.connection_master)
        thread_master.daemon = True
        thread_master.start()

        print(f"[ROUTER {self.__name}] Écoute sur {self.__host}:{self.__port}")
        print(f"[ROUTER {self.__name}] Clé publique: {self.__public_key}")
        print(f"[ROUTER {self.__name}] Clé privée: {self.__prv_key}")
        
        self.new_connection()

    def connection(self, host: str, port: int):
        co = socket.socket()
        co.connect((host, port))
        return co

    def connection_master(self):
        while True:
            if not self.__master_host or not self.__master_port:
                time.sleep(1)
                continue

            co_master = None
            try:
                co_master = self.connection(self.__master_host, self.__master_port)
                e, n = self.__public_key
                public_key_str = f"{e}:{n}"
                co_master.send(f"ROUTER::{self.__name}::{self.get_Host_IP()}::{self.__port}::{public_key_str}".encode('utf-8'))

                while True:
                    data = co_master.recv(1024)
                    if not data: break
                    if data.decode('utf-8') == "SHUTDOWN": break

            except Exception as e:
                print(f"[ERREUR MASTER] {type(e).__name__}: {e}")
            finally:
                if co_master:
                    co_master.close()
                time.sleep(5)  # on attend avant de retenter


    def new_connection(self):
        while True:
            conn, address = self.__router_socket.accept()
            print(f"[CONNEXION] Nouvelle connexion depuis {address}")
            self.__list_connected.append(conn)
            
            thread_client = threading.Thread(target=self.routage, args=(conn, address))
            thread_client.daemon = True
            thread_client.start()

    def routage(self, conn, addr):
        try:
            full_message = self.receive_full_message(conn)

            if not full_message:
                print(f"[{addr}] Message vide ou incomplet")
                return

            # Déchiffrer
            next_ip, next_port, rest = self.decrypt_message(full_message)

            # Forward au prochain saut en chunks
            if next_ip and next_port:
                print(f"[TRANSFERT] Vers {next_ip}:{next_port}")
                chunks = self.chunk_message(rest)
                forward_socket = socket.socket()
                forward_socket.connect((next_ip, next_port))
                for chunk in chunks:
                    forward_socket.send(chunk)
                    print(chunk)
                    time.sleep(2)
                forward_socket.close()
                print("[OK] Message transféré en chunks")

        except ValueError as e:
            print(f"[ERREUR FORMAT] {e}")
        except Exception as e:
            print(f"[ERREUR ROUTAGE] {type(e).__name__}: {e}")
        finally:
            conn.close()

    def chunk_message(self, message: str, max_chunk_size=1024):
        data = message.encode()
        msg_id = random.randint(0,10000)
        chunks = []
        total_chunks = (len(data) + max_chunk_size - 1) // max_chunk_size

        for i in range(total_chunks):
            start = i * max_chunk_size
            end = start + max_chunk_size
            chunk_data = data[start:end]
            header = f"{msg_id}|{i}|{total_chunks}|".encode()
            chunks.append(header + chunk_data)

        return chunks

    def receive_full_message(self, conn):
        while True:
            data = conn.recv(2048)
            if not data:
                break
            print(data)
            try:
                header, payload = data.split(b"|", 3)[0:3], data.split(b"|", 3)[3]
                msg_id = int(header[0])
                chunk_index = int(header[1])
                total_chunks = int(header[2])
            except:
                print("[ERREUR] Chunk invalide reçu")
                return None

            if msg_id not in self.__chunk_buffer:
                self.__chunk_buffer[msg_id] = {
                    "total": total_chunks,
                    "chunks": {}
                }

            self.__chunk_buffer[msg_id]["chunks"][chunk_index] = payload

            if len(self.__chunk_buffer[msg_id]["chunks"]) == total_chunks:
                chunks = self.__chunk_buffer[msg_id]["chunks"]
                full_data = b"".join(chunks[i] for i in range(total_chunks))
                del self.__chunk_buffer[msg_id]
                return full_data.decode("utf-8")

        return None

    def decrypt_message(self, encrypted_message: str):
        print(f"[DECRYPT] Tentative de déchiffrement...")
        print(f"[DECRYPT] Ma clé privée: {self.__prv_key}")
        
        try:
            # Déchiffrer directement
            decrypted = self.__crypto.decrypt(encrypted_message)
            print(f"[DECRYPT] Succès ! Déchiffré: {decrypted[:100]}...")
            
            # Parser le résultat déchiffré
            parts = decrypted.split('::', 2)
            
            if len(parts) < 3:
                raise ValueError(f"Format invalide: {len(parts)} parties au lieu de 3")
            
            next_ip = parts[0]
            next_port = parts[1]
            next_content = parts[2]
            
            return next_ip, int(next_port), next_content
            
        except Exception as e:
            print(f"[ERREUR DECRYPT] {type(e).__name__}: {e}")
            raise
    
    def terminal_loop(self):
        while True:
            try:
                cmd = str(input("router> ").strip())
                if not cmd:
                    continue
                if cmd.startswith("/"):
                    self.console_cmd(cmd)
                else:
                    print("[INFO] Le router ne peut pas envoyer de messages.")
            except KeyboardInterrupt:
                print("\n[STOP] Arrêt du router.")
                break
    
    def console_cmd(self, cmd: str):
        parts = cmd.split()

        match parts:
            case ["/ip", "master", ip]:
                self.__master_host = ip
                print(f"[INFO] IP master définie à {ip}")

            case ["/port", "master", port]:
                self.__master_port = int(port)
                print(f"[INFO] Port master défini à {port}")

            case ["/status"]:
                print("---- ROUTER STATUS ----")
                print(f"Name         : {self.__name}")
                print(f"Listening    : {self.__host}:{self.__port}")
                print(f"Master       : {getattr(self, '_router__master_host', None)}:{getattr(self, '_router__master_port', None)}")
                print(f"Connexions   : {len(self.__list_connected)}")

            case ["/start", "master"]:
                print("[INFO] Connexion master demandée.")
                threading.Thread(target=self.connection_master, daemon=True).start()

            case ["/help"]:
                print("""
                    Commandes disponibles:
                    /ip master <ip>       → définir IP du master
                    /port master <port>   → définir port du master
                    /start master         → forcer connexion master
                    /status               → état du router
                    /stop                 → arrêter le router
                    """)

            case ["/stop"]:
                print("[STOP] Fermeture du router.")
                self.__router_socket.close()
                sys.exit(0)

            case _:
                print("""
                    Commandes disponibles:
                    /ip master <ip>       → définir IP du master
                    /port master <port>   → définir port du master
                    /start master         → forcer connexion master
                    /status               → état du router
                    /stop                 → arrêter le router
                    """)
        
            
if __name__ == "__main__":
    name = str(input("name >> "))
    port = int(input("port >> "))
    router_instance = router(name=name, port=port)
    router_instance.start()