import threading
import pymysql
import sys
from .AcceptHandler import AcceptHandler
from .ClientHandler import ClientHandler

class MasterCore:
    def __init__(self, host='0.0.0.0', port=None):
        self.host = host
        self.port = port
        self.running = True
        self.lock = threading.Lock()
        self.list_clients = []
        self.list_routers = []
        self.db_connected = False
        self.accept_handler = None # Initialisé au start
        self.client_handler = ClientHandler(self)
        self.db_connected = False
        target_db_ip = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'

        self.db_config = {
            'host': target_db_ip,
            'user': 'root',
            'password': '',
            'database': 'oignon_db',
            'autocommit': True
        }
        self.db_connected = False
        self.init_db()

    def start(self):
        """Démarre le serveur sur le port configuré"""
        if self.port is None:
            return
        self.accept_handler = AcceptHandler(self)
        threading.Thread(target=self.accept_handler.start_server, daemon=True).start()
        print(f"[MASTER] Serveur lancé sur {self.host}:{self.port}")

    def shutdown_network(self):
        self.running = False
        with self.lock:
            for node in self.list_routers + self.list_clients:
                try:
                    if 'socket' in node:
                        node['socket'].send("SHUTDOWN".encode('utf-8'))
                        node['socket'].close()
                except: pass

    def init_db(self):
        # Création de la base
        conn = pymysql.connect(host=self.db_config['host'], user=self.db_config['user'],
                               password=self.db_config['password'])
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_config['database']}")
        conn.close()

        # Création de la table
        conn = pymysql.connect(**self.db_config)
        cursor = conn.cursor()
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS logs (
                           id INT AUTO_INCREMENT PRIMARY KEY,
                           sender VARCHAR(255),
                           receiver VARCHAR(255),
                           content TEXT,
                           timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                           )
                       """)
        conn.close()

        # OBLIGATOIRE : C'est ce flag qui fait passer le rectangle au VERT
        self.db_connected = True

    def log_message_to_db(self, sender, receiver, msg):
        if self.db_connected:
            conn = pymysql.connect(**self.db_config)
            cursor = conn.cursor()
            sql = "INSERT INTO logs (sender, receiver, content) VALUES (%s, %s, %s)"
            cursor.execute(sql, (sender, receiver, msg))
            conn.close()