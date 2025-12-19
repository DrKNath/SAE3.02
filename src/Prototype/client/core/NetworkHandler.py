import socket
import threading

class NetworkHandler:
    def __init__(self, core):
        self.core = core

    def start_server(self):
        server = socket.socket()
        print(self.core.host, self.core.port)
        server.bind((self.core.host, self.core.port))
        server.listen(5)
        print(f"[INFO] Client écoute sur {self.core.host}:{self.core.port}")
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
