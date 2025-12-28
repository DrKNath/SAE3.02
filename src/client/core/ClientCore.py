import threading
import sys
from .MasterConnection import MasterConnection
from .OnionRouter import OnionRouter
from .NetworkHandler import NetworkHandler

class ClientCore:
    def __init__(self, name, host='0.0.0.0', port=0):
        self.name = name
        self.host = host
        self.port = port
        self.running = True
        self.lock = threading.Lock()
        self.list_clients = []
        self.list_routers = []
        self.route = []
        self.master_conn = MasterConnection(self)
        self.network_handler = NetworkHandler(self)
        self.onion_router = OnionRouter(self)

    def start(self):
        threading.Thread(target=self.master_conn.connect_master, daemon=True).start()
        threading.Thread(target=self.network_handler.start_server, daemon=True).start()

    def stop(self):
        self.running = False

        self.master_conn.stop()
        self.network_handler.stop()

        print("[INFO] Client déconnecté et arrêté.")
        sys.exit(0)