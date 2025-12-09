import socket
import threading
from crypto import crypto

class router:
    def __init__(self, name: str, host: str = '0.0.0.0', port: int = 0):
        self.__name = name
        self.__host = host
        self.__port = port
        self.__crypto = crypto()
        self.__public_key = self.__crypto.public
        self.__prv_key = self.__crypto.prive
        self.__router_socket = socket.socket()
        self.__list_connected = []

    def start(self):
        # Thread Master co
        thread_master = threading.Thread(target=self.connection_master)
        thread_master.daemon = True
        thread_master.start()
        
        # Socket serveur pour écouter les clients
        self.__router_socket.bind((self.__host, self.__port))
        self.__router_socket.listen(5)
        print(f"[ROUTER {self.__name}] Écoute sur {self.__host}:{self.__port}")
        print(f"[ROUTER {self.__name}] Clé publique: {self.__public_key}")
        print(f"[ROUTER {self.__name}] Clé privée: {self.__prv_key}")
        
        self.new_connection()

    def connection(self, host: str, port: int):
        co = socket.socket()
        co.connect((host, port))
        return co

    def connection_master(self):
        co_master = self.connection('192.0.0.2', 10001)
        e, n = self.__public_key
        public_key_str = f"{e}:{n}"
        co_master.send(f"ROUTER::{self.__name}::{'192.0.0.2'}::{self.__port}::{public_key_str}".encode('utf-8'))
        
        # Boucle infinie pour maintenir le socket ouvert
        try:
            while True:
                # Ici tu peux écouter des messages du master si besoin
                data = co_master.recv(1024)
                if not data:
                    break  # master a fermé la connexion
        except Exception as e:
            print(f"[ERREUR MASTER] {e}")
        finally:
            co_master.close()

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
            # IMPORTANT: recevoir EN UNE SEULE FOIS tout le message
            message = conn.recv(4096).decode('utf-8')  # Augmenter la taille buffer
            
            if not message:
                print(f"[{addr}] Message vide reçu")
                return
            
            print(f"[REÇU DE {addr}] Taille: {len(message)} caractères")
            print(f"[REÇU] Début: {message[:100]}...")
            
            # Déchiffrer le message
            next_ip, next_port, rest = self.decrypt_message(message)
            
            print(f"[DÉCHIFFRÉ] Next hop: {next_ip}:{next_port}")
            print(f"[DÉCHIFFRÉ] Contenu à transférer: {len(rest)} caractères")
            
            # Transférer au prochain saut
            if next_ip and next_port:
                print(f"[TRANSFERT] Vers {next_ip}:{next_port}")
                forward_socket = socket.socket()
                forward_socket.connect((next_ip, next_port))
                forward_socket.send(rest.encode('utf-8'))
                forward_socket.close()
                print(f"[OK] Transféré avec succès")
                
        except ValueError as e:
            print(f"[ERREUR FORMAT] {e}")
        except Exception as e:
            print(f"[ERREUR ROUTAGE] {type(e).__name__}: {e}")
        finally:
            conn.close()

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


if __name__ == "__main__":
    name = str(input("name >> "))
    port = int(input("port >> "))
    router_instance = router(name=name, port=port)
    router_instance.start()