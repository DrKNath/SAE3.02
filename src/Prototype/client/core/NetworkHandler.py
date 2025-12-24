import socket
import threading


class NetworkHandler:
    def __init__(self, core):
        self.core = core
        self.server = None

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
            print(f"\n[MSG REÇU] {msg}\n>> ", end="")
            return self.core.ui_handler.notify_received_message(msg)
        except:
            pass
        cli.close()

    def send_to_first_router(self, onion):
        if not self.core.route:
            return
        first = self.core.route[0]
        try:
            sock = socket.socket()
            sock.connect((first["ip"], first["port"]))
            sock.send(onion.encode())
            sock.close()
        except:
            print("[ERREUR] Impossible d’envoyer au premier router.")