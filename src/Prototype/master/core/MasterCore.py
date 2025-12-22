import threading
from .AcceptHandler import AcceptHandler
from .ClientHandler import ClientHandler


class MasterCore:
    def __init__(self, host='0.0.0.0', port=0):
        self.host = host
        self.port = port

        self.running = True
        self.lock = threading.Lock()

        # État partagé
        self.list_clients = []
        self.list_routers = []

        # Modules
        self.accept_handler = AcceptHandler(self)
        self.client_handler = ClientHandler(self)

    def start(self):
        # Thread accept socket
        threading.Thread(
            target=self.accept_handler.start_server,
            daemon=True
        ).start()

        print(f"[MASTER] Démarré sur {self.host}:{self.port}")

    def stop(self):
        print("[INFO] Arrêt du master...")
        self.running = False

        self.accept_handler.stop()
        self.client_handler.stop()

        print("[INFO] Master arrêté.")
        exit(0)
