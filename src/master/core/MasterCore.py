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

        # Récupération des paramètres via la console (IP, User, Password)
        # Usage : python -m master.main 192.168.1.120 root toto123
        target_db_ip = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
        db_user = sys.argv[2] if len(sys.argv) > 2 else 'root'
        db_password = sys.argv[3] if len(sys.argv) > 3 else ''

        self.db_config = {
            'host': target_db_ip,
            'user': db_user,
            'password': db_password,
            'database': 'oignon_db',
            'autocommit': True,
            'connect_timeout': 5
        }

        self.db_connected = False
        self.client_handler = ClientHandler(self)
        self.init_db_connection()

    def init_db_connection(self):
        """Vérifie la connexion à la BDD MariaDB sans créer de tables"""
        try:
            conn = pymysql.connect(**self.db_config)
            conn.close()
            self.db_connected = True
            print(f"[MASTER] Connecté à la BDD MariaDB sur {self.db_config['host']}")
        except Exception as e:
            self.db_connected = False
            print(f"[DATABASE ERROR] Connexion impossible : {e}")

    def log_message_to_db(self, sender, receiver, msg):
        """Ajoute une entrée dans l'historique des logs"""
        if self.db_connected:
            try:
                conn = pymysql.connect(**self.db_config)
                cursor = conn.cursor()
                sql = "INSERT INTO logs (sender, receiver, content) VALUES (%s, %s, %s)"
                cursor.execute(sql, (sender, receiver, msg))
                conn.close()
            except Exception as e:
                print(f"[DATABASE ERROR] Erreur log : {e}")

    def db_manage_active_node(self, name, ntype, ip, port, pubkey=None):
        """Met à jour un nœud (Client/Routeur) dans la table active_nodes """
        if self.db_connected:
            try:
                conn = pymysql.connect(**self.db_config)
                cursor = conn.cursor()
                sql = "REPLACE INTO active_nodes (name, type, ip, port, public_key) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, (name, ntype, ip, port, pubkey))
                conn.close()
            except Exception as e:
                print(f"[DATABASE ERROR] Erreur ajout nœud : {e}")

    def db_remove_active_node(self, name):
        """Supprime un nœud de la BDD lors de sa déconnexion"""
        if self.db_connected:
            try:
                conn = pymysql.connect(**self.db_config)
                cursor = conn.cursor()
                sql = "DELETE FROM active_nodes WHERE name = %s"
                cursor.execute(sql, (name,))
                conn.close()
            except Exception as e:
                print(f"[DATABASE ERROR] Erreur suppression nœud : {e}")

    def start(self):
        if self.port is None: return
        self.accept_handler = AcceptHandler(self)
        threading.Thread(target=self.accept_handler.start_server, daemon=True).start()
