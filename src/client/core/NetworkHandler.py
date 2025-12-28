import socket
import threading
import time
import random

class NetworkHandler:
    def __init__(self, core):
        self.core = core
        self.server = None

        #Partie chunk
        self.MAX_CHUNK_SIZE = 1024  #taille max par chunk 
        self._msg_counter:int = random.randint(0, 10000)  

    def start_server(self):
        server = socket.socket()
        print(self.core.host, self.core.port)
        server.bind((self.core.host, self.core.port))
        server.listen(5)
        print(f"[INFO] Client écoute sur {self.core.host}:{self.core.port}")
        while self.core.running:
            try:
                cli, addr = server.accept()
                threading.Thread(target=self.handle_incoming, args=(cli, addr), daemon=True).start()
            except socket.timeout:
                continue
            except:
                break
        print("[INFO] Serveur réseau arrêté")

    def stop(self):
        if self.server:
            try:
                self.server.close()
            except:
                pass

    def handle_incoming(self, cli, addr):
        try:
            msg = cli.recv(4096).decode()
            return self.core.ui_handler.notify_received_message(msg)
        except:
            pass
        cli.close()

    def _next_msg_id(self):
        self._msg_counter += 1
        return self._msg_counter

    def chunk_message(self, data: bytes):
        msg_id = self._next_msg_id()
        chunks = []

        total_chunks = (len(data) + self.MAX_CHUNK_SIZE - 1) // self.MAX_CHUNK_SIZE

        for i in range(total_chunks):
            start = i * self.MAX_CHUNK_SIZE
            end = start + self.MAX_CHUNK_SIZE
            chunk_data = data[start:end]

            header = f"{msg_id}|{i}|{total_chunks}|".encode()
            chunks.append(header + chunk_data)

        return chunks

    def send_to_first_router(self, onion: bytes):
        if not self.core.route:
            return
        first = self.core.route[0]
        chunk = self.chunk_message(onion)
        print(chunk)
        try:
            sock = socket.socket()
            sock.connect((first["ip"], first["port"]))
            for chunks in chunk:
                print(chunks)
                sock.send(chunks)
                time.sleep(3)
            
            sock.close()
        except:
            print("[ERREUR] Impossible d’envoyer au premier router.")