import threading
from MasterConnection import MasterConnection
from OnionRouter import OnionRouter
from NetworkHandler import NetworkHandler
from UIHandler import UIHandler

class ClientCore:
    def __init__(self, name, host='0.0.0.0', port=0):
        self.name = name
        self.host = host
        self.port = port

        self.list_clients = []
        self.list_routers = []
        self.route = []

        self.lock = threading.Lock()
        self.destination_ip = '192.0.0.2'
        self.destination_port = 30002

        # Modules
        self.master_conn = MasterConnection(self)
        self.onion_router = OnionRouter(self)
        self.network_handler = NetworkHandler(self)
        self.ui_handler = UIHandler(self)

    def start(self):
        # Connexion master
        threading.Thread(target=self.master_conn.connect_master, daemon=True).start()
        # Serveur réception messages
        threading.Thread(target=self.network_handler.start_server, daemon=True).start()
        # Démarre l’UI terminal
        self.ui_handler.start()
