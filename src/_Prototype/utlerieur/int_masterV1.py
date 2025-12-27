import sys
import time
import socket
import threading
import mysql.connector as db_connector
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLineEdit, QTextEdit, QPushButton,
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox)
from PyQt6.QtCore import (QThread, pyqtSignal, Qt)

MYSQL_CONNECTOR = db_connector
if not MYSQL_CONNECTOR:
    print("ATTENTION: Le module 'mysql-connector-python' est manquant.")


class DBManager:
    def __init__(self, host, user, password, database, log_callback):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.log_callback = log_callback
        if MYSQL_CONNECTOR:
            self.connect()
        else:
            self.log_callback("[ERREUR FATALE] Driver BDD manquant.")

    def log(self, msg):
        self.log_callback(msg)

    def connect(self):
        if not MYSQL_CONNECTOR: return False
        try:
            self.connection = MYSQL_CONNECTOR.connect(
                host=self.host, user=self.user, password=self.password,
                database=self.database, connection_timeout=5
            )
            return True
        except MYSQL_CONNECTOR.Error as err:
            self.log(f"[DB] Erreur de connexion: {err.msg}")
            self.connection = None
            return False

    def execute_query(self, query, params=None, fetch=False):
        if not self.connection or not self.connection.is_connected():
            if not self.connect(): return None

        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params or ())
            if fetch:
                return cursor.fetchall()
            else:
                self.connection.commit()
                return True
        except MYSQL_CONNECTOR.Error as err:
            self.log(f"[ERREUR SQL] Code {err.errno}: {err.msg}")
            return False
        finally:
            cursor.close()

    def create_tables_if_not_exists(self):
        create_script = """
        CREATE TABLE IF NOT EXISTS NOEUDS (
            id_noeud VARCHAR(50) PRIMARY KEY, type_noeud VARCHAR(10) NOT NULL,
            adresse_ip VARCHAR(15) NOT NULL, port_ecoute INT NOT NULL,
            statut VARCHAR(10) NOT NULL DEFAULT 'INACTIF'
        );
        CREATE TABLE IF NOT EXISTS CLES_CHIFFREMENT (
            id_cle INT AUTO_INCREMENT PRIMARY KEY, id_noeud VARCHAR(50) NOT NULL,
            cle_publique TEXT NOT NULL, cle_privee TEXT NOT NULL,
            date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_noeud) REFERENCES NOEUDS(id_noeud)
        );
        CREATE TABLE IF NOT EXISTS TABLE_ROUTAGE (
            id_route INT AUTO_INCREMENT PRIMARY KEY, routeur_source VARCHAR(50) NOT NULL,
            routeur_suivant VARCHAR(50) NOT NULL, description VARCHAR(255),
            FOREIGN KEY (routeur_source) REFERENCES NOEUDS(id_noeud),
            FOREIGN KEY (routeur_suivant) REFERENCES NOEUDS(id_noeud)
        );
        """
        return all(self.execute_query(stmt) for stmt in create_script.split(';')[:-1] if stmt.strip())

    def clear_all_data(self):
        if not self.connection or not self.connection.is_connected(): return False
        self.execute_query("SET FOREIGN_KEY_CHECKS = 0;")
        tables = ["TABLE_ROUTAGE", "CLES_CHIFFREMENT", "NOEUDS"]
        success = all(self.execute_query(f"TRUNCATE TABLE {table};") for table in tables)
        self.execute_query("SET FOREIGN_KEY_CHECKS = 1;")
        return success

    def insert_test_data(self):
        if not self.connection or not self.connection.is_connected(): return False
        self.clear_all_data()

        nodes = [('Master', 'MASTER', '127.0.0.1', 8000), ('R1', 'ROUTER', '192.168.1.10', 5001),
                 ('R2', 'ROUTER', '192.168.1.11', 5002), ('R3', 'ROUTER', '192.168.1.12', 5003),
                 ('ClientA', 'CLIENT', '192.168.1.20', 6001), ('ClientB', 'CLIENT', '192.168.1.21', 6002)]
        insert_node_query = "INSERT INTO NOEUDS (id_noeud, type_noeud, adresse_ip, port_ecoute, statut) VALUES (%s, %s, %s, %s, 'INACTIF');"
        for node in nodes: self.execute_query(insert_node_query, node)

        keys = [('R1', 'PUB_R1_KEY_SIMULEE', 'PRIV_R1_KEY_SIMULEE'),
                ('R2', 'PUB_R2_KEY_SIMULEE', 'PRIV_R2_KEY_SIMULEE'),
                ('R3', 'PUB_R3_KEY_SIMULEE', 'PRIV_R3_KEY_SIMULEE')]
        insert_key_query = "INSERT INTO CLES_CHIFFREMENT (id_noeud, cle_publique, cle_privee) VALUES (%s, %s, %s);"
        for key in keys: self.execute_query(insert_key_query, key)

        routes = [('R1', 'R2', 'Route R1 vers R2'), ('R2', 'R3', 'Route R2 vers R3'),
                  ('R3', 'ClientB', 'Route finale vers ClientB'),
                  ('ClientA', 'R1', 'ClientA envoie à R1 pour commencer le circuit')]
        insert_route_query = "INSERT INTO TABLE_ROUTAGE (routeur_source, routeur_suivant, description) VALUES (%s, %s, %s);"
        for route in routes: self.execute_query(insert_route_query, route)

        return True

    def fetch_nodes(self):
        query = "SELECT id_noeud, adresse_ip, port_ecoute, statut FROM NOEUDS WHERE type_noeud IN ('ROUTER', 'CLIENT');"
        return self.execute_query(query, fetch=True) or []

    def update_node_status(self, node_id, status):
        query = "UPDATE NOEUDS SET statut = %s WHERE id_noeud = %s;"
        return self.execute_query(query, (status, node_id))


class MasterCore:
    def __init__(self, host, port, db_manager, log_callback, update_callback):
        self.host = host
        self.port = port
        self.db = db_manager
        self.log_cb = log_callback
        self.update_cb = update_callback

        self.clients = {}
        self.routers = {}
        self.is_running = False

    def log(self, msg):
        self.log_cb(msg)

    def start(self):
        if self.is_running: return
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.is_running = True
            self.log(f"[CTRL] Serveur démarré sur {self.host}:{self.port}.")

            while self.is_running:
                try:
                    self.server_socket.settimeout(0.5)
                    conn, addr = self.server_socket.accept()

                    thread = threading.Thread(target=self.handle_connection, args=(conn, addr))
                    thread.daemon = True
                    thread.start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.is_running: self.log(f"[ERREUR] Erreur dans acceptation: {e}")
                    break
        except Exception as e:
            self.log(f"[ERREUR FATALE] Échec du démarrage: {e}")
            self.stop()

    def stop(self):
        self.is_running = False
        self.log("[CTRL] Arrêt du serveur en cours...")
        try:
            if hasattr(self, 'server_socket'): self.server_socket.close()
            for sock in list(self.clients.keys()) + list(self.routers.keys()):
                self.remove_socket(sock)
        except Exception as e:
            self.log(f"[ERREUR] Erreur lors de l'arrêt: {e}")
        self.log("[CTRL] Serveur Master arrêté.")

    def handle_connection(self, sock, addr):
        name = "Inconnu"
        try:
            sock.settimeout(3.0)
            message = sock.recv(1024).decode('utf-8')

            if not message:
                self.log(f"[DC] Connexion initiale vide de {addr}");
                return

            parsed = self._parse_identification(message)
            c_type = parsed.get('type')
            name = parsed.get('name', 'Inconnu')

            if c_type in ['CLIENT', 'ROUTER']:
                self._register_node(sock, name, c_type)
            else:
                self.log(f"[WARN] Type inconnu reçu de {addr}: {c_type}")

            while self.is_running:
                heartbeat = sock.recv(1024)
                if not heartbeat:
                    self.log(f"[DC] Déconnexion détectée par heartbeat: {name} / {addr}")
                    break
                time.sleep(0.1)

        except socket.timeout:
            self.log(f"[DC] Timeout d'identification pour {addr}.")
        except Exception as e:
            self.log(f"[ERR] Problème avec {addr} ({name}) : {e}")
        finally:
            self.remove_socket(sock)

    def _register_node(self, sock, name, c_type):
        self.db.update_node_status(name, 'ACTIF')
        self.update_cb()

        if c_type == 'CLIENT':
            self.clients[sock] = name
            self.log(f"[CONN] Client {name} connecté.")
            sock.send(self.serialize_lists().encode('utf-8'))
        elif c_type == 'ROUTER':
            self.routers[sock] = name
            self.log(f"[CONN] Routeur {name} connecté.")

        self.broadcast_lists_to_clients()

    def _parse_identification(self, msg):
        parts = msg.split("::")
        if len(parts) < 4: return {'type': 'UNKNOWN'}

        c_type = parts[0]
        name = parts[1]

        return {'type': c_type, 'name': name}

    def serialize_lists(self):
        router_keys = {}
        key_results = self.db.execute_query("SELECT id_noeud, cle_publique FROM CLES_CHIFFREMENT;", fetch=True)
        if key_results:
            router_keys = {row[0]: row[1] for row in key_results}

        nodes = self.db.execute_query(
            "SELECT id_noeud, type_noeud, adresse_ip, port_ecoute FROM NOEUDS WHERE type_noeud IN ('CLIENT', 'ROUTER');",
            fetch=True
        )

        clients_data = []
        routers_data = []

        for name, type_noeud, ip, port in nodes:
            if type_noeud == 'CLIENT':
                clients_data.append(f"{name}::{ip}::{port}")
            elif type_noeud == 'ROUTER':
                pubkey = router_keys.get(name, "NO_KEY")
                routers_data.append(f"{name}::{ip}::{port}::{pubkey}")

        clients_str = ";;".join(clients_data)
        routers_str = ";;".join(routers_data)

        return f"CLIENTS:{clients_str}||ROUTERS:{routers_str}"

    def broadcast_lists_to_clients(self):
        msg = self.serialize_lists()

        for client_socket, name in list(self.clients.items()):
            try:
                client_socket.send(msg.encode('utf-8'))
            except Exception:
                self.log(f"[WARN] Impossible d'envoyer à {name}. Déconnexion forcée.")
                self.remove_socket(client_socket)

    def remove_socket(self, sock):
        removed_name = None
        removed_type = None

        if sock in self.clients:
            removed_name = self.clients.pop(sock)
            removed_type = 'CLIENT'
        elif sock in self.routers:
            removed_name = self.routers.pop(sock)
            removed_type = 'ROUTER'

        if removed_name:
            self.db.update_node_status(removed_name, 'INACTIF')
            try:
                sock.close()
            except:
                pass

            self.log(f"[DC] {removed_type} {removed_name} déconnecté.")

            self.update_cb()
            self.broadcast_lists_to_clients()


class MasterServerThread(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, host, port, db_manager, ui_update_callback):
        super().__init__()
        self.master_core = MasterCore(host, port, db_manager, self.log_signal.emit, ui_update_callback)

    def run(self):
        self.master_core.start()

    def stop_server(self):
        self.master_core.stop()


class MasterWindow(QMainWindow):
    log_signal = pyqtSignal(str)
    update_topology_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Master Supervisor - Onion Router")
        self.setGeometry(200, 200, 900, 700)

        self.db_manager = None
        self.master_server_thread = None

        self.log_widget = QTextEdit()
        self.log_signal.connect(self.log_widget.append)
        self.update_topology_signal.connect(self.update_topology_table)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.setup_ui()
        self.connecter_bdd()

    def setup_ui(self):

        db_config_group = QVBoxLayout()
        db_config_group.addWidget(QLabel("<b>Configuration MariaDB:</b>"))
        config_layout = QHBoxLayout()

        config_layout.addWidget(QLabel("Host:"))
        self.db_host = QLineEdit("127.0.0.1")
        config_layout.addWidget(self.db_host)

        config_layout.addWidget(QLabel("User:"))
        self.db_user = QLineEdit("onion_user")
        config_layout.addWidget(self.db_user)

        config_layout.addWidget(QLabel("Pass:"))
        self.db_pass = QLineEdit("votre_mot_de_passe")
        self.db_pass.setEchoMode(QLineEdit.EchoMode.Password)
        config_layout.addWidget(self.db_pass)

        self.connect_db_btn = QPushButton("Reconnecter BDD")
        self.connect_db_btn.clicked.connect(self.connecter_bdd)
        config_layout.addWidget(self.connect_db_btn)

        db_config_group.addLayout(config_layout)
        self.layout.addLayout(db_config_group)

        control_layout = QHBoxLayout()

        self.generate_keys_btn = QPushButton("1. CRÉER TABLES & INSERER DONNÉES TEST")
        self.generate_keys_btn.clicked.connect(self.generer_cles_et_routes)
        self.generate_keys_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        control_layout.addWidget(self.generate_keys_btn)

        self.start_master_btn = QPushButton("2. Démarrer Serveur Master (10001)")
        self.start_master_btn.clicked.connect(self.toggle_master_server)
        self.start_master_btn.setStyleSheet("background-color: #2196F3; color: white;")
        control_layout.addWidget(self.start_master_btn)

        self.clear_data_btn = QPushButton("VIDER BDD")
        self.clear_data_btn.setStyleSheet("background-color: darkred; color: white;")
        self.clear_data_btn.clicked.connect(self.vider_bdd)
        control_layout.addWidget(self.clear_data_btn)

        self.layout.addLayout(control_layout)

        self.layout.addWidget(QLabel("<b>Topologie Réseau (Routeurs & Clients):</b>"))
        self.topology_table = QTableWidget()
        self.topology_table.setColumnCount(4)
        self.topology_table.setHorizontalHeaderLabels(["ID Noeud", "Adresse IP", "Port Écoute", "Statut"])
        self.topology_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.topology_table)

        self.layout.addWidget(QLabel("<b>Journal des Événements et Logs:</b>"))
        self.log_widget.setReadOnly(True)
        self.layout.addWidget(self.log_widget)

    def toggle_master_server(self):
        if not self.db_manager or not self.db_manager.connection:
            QMessageBox.warning(self, "Erreur BDD", "Veuillez vous connecter à la BDD et créer les tables d'abord.")
            return

        if self.master_server_thread and self.master_server_thread.isRunning():
            self.master_server_thread.stop_server()
            self.master_server_thread.wait()
            self.start_master_btn.setText("2. Démarrer Serveur Master (10001)")
            self.start_master_btn.setStyleSheet("background-color: #2196F3; color: white;")
            self.log_message("[CTRL] Serveur Master arrêté.")
            self.update_topology_table()
        else:
            master_host = '0.0.0.0'
            master_port = 10001

            ui_update_callback = self.update_topology_signal.emit

            self.master_server_thread = MasterServerThread(
                master_host,
                master_port,
                self.db_manager,
                ui_update_callback
            )
            self.master_server_thread.log_signal.connect(self.log_widget.append)
            self.master_server_thread.start()

            self.start_master_btn.setText("3. Arrêter Serveur Master")
            self.start_master_btn.setStyleSheet("background-color: #e74c3c; color: white;")
            self.log_message(f"[CTRL] Démarrage du serveur Master sur {master_host}:{master_port}...")

    def log_message(self, message):
        self.log_signal.emit(message)

    def connecter_bdd(self):
        if not MYSQL_CONNECTOR:
            self.log_message("[ERREUR FATALE] Le driver 'mysql-connector-python' est manquant.")
            return False

        if self.db_manager: self.db_manager.close()

        host = self.db_host.text()
        user = self.db_user.text()
        password = self.db_pass.text()
        db_name = "onion_router_db"

        self.log_message(f"[DB] Tentative de connexion à {host}@{db_name}...")
        self.db_manager = DBManager(host, user, password, db_name, log_callback=self.log_message)

        if self.db_manager.connection:
            self.log_message("[DB] Connexion MariaDB réussie.")
            self.update_topology_table()
            return True
        else:
            self.log_message("[ERREUR DB] Échec de la connexion à MariaDB.")
            return False

    def generer_cles_et_routes(self):
        if not self.db_manager or not self.db_manager.connection:
            self.log_message("[ERREUR DB] Non connecté à la BDD.")
            return

        self.log_message("[DB] Création/Insertion des données de test...")
        if self.db_manager.create_tables_if_not_exists() and self.db_manager.insert_test_data():
            self.log_message("[DB] Topologie et clés créées avec succès.")
            self.update_topology_table()
        else:
            self.log_message("[ERREUR DB] Échec de la création/insertion des données.")

    def vider_bdd(self):
        if not self.db_manager or not self.db_manager.connection:
            self.log_message("[ERREUR DB] Non connecté à la BDD.")
            return

        reply = QMessageBox.question(self, 'Confirmation',
                                     "Êtes-vous sûr de vouloir supprimer TOUTES les données ?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.log_message("[DB] Suppression de toutes les données en cours...")
            if self.db_manager.clear_all_data():
                self.log_message("[DB] Suppression des données effectuée avec succès.")
                self.update_topology_table()
            else:
                self.log_message("[ERREUR DB] Échec de la suppression des données.")
        else:
            self.log_message("[DB] Suppression annulée.")

    def update_topology_table(self):
        if not self.db_manager or not self.db_manager.connection:
            self.topology_table.setRowCount(0)
            return

        nodes = self.db_manager.fetch_nodes()

        self.topology_table.setRowCount(len(nodes))
        for row, node in enumerate(nodes):
            self.topology_table.setItem(row, 0, QTableWidgetItem(node[0]))
            self.topology_table.setItem(row, 1, QTableWidgetItem(node[1]))
            self.topology_table.setItem(row, 2, QTableWidgetItem(str(node[2])))

            status_item = QTableWidgetItem(node[3])
            color = Qt.GlobalColor.darkGreen if node[3] == 'ACTIF' else Qt.GlobalColor.red
            status_item.setForeground(color)

            self.topology_table.setItem(row, 3, status_item)

    def closeEvent(self, event):
        if self.master_server_thread and self.master_server_thread.isRunning():
            self.master_server_thread.stop_server()
            self.master_server_thread.wait()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    master_gui = MasterWindow()
    master_gui.show()
    sys.exit(app.exec())
