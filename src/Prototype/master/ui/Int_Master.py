from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
                             QLabel, QTextEdit, QTableWidget, QTableWidgetItem,
                             QHeaderView, QPushButton)
from PyQt6.QtCore import QTimer, Qt


class MasterGUI(QMainWindow):
    def __init__(self, handler):
        super().__init__()
        self.handler = handler
        self.handler.set_ui(self)  # Le handler prend le contrôle de cette fenêtre

        self.setWindowTitle("SAÉ 3.02 - SUPERVISEUR RÉSEAU OIGNON")
        self.resize(800, 600)
        self.setStyleSheet("background-color: #1e1e2e; color: #cdd6f4;")

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # Bouton simple : délègue une commande au handler sans rien faire lui-même
        self.btn_status = QPushButton("DEMANDER L'INVENTAIRE DES NŒUDS")
        self.btn_status.setStyleSheet("background-color: #89b4fa; color: #11111b; font-weight: bold; padding: 10px;")
        self.btn_status.clicked.connect(lambda: self.handler.handle_command("/routers"))
        main_layout.addWidget(self.btn_status)

        self.label_stats = QLabel("STATUT : EN ATTENTE DE DONNÉES...")
        self.label_stats.setStyleSheet("font-size: 14px; font-weight: bold; color: #fab387; margin: 5px;")
        main_layout.addWidget(self.label_stats)

        self.table_nodes = QTableWidget(0, 3)
        self.table_nodes.setHorizontalHeaderLabels(["Type", "Adresse IP", "Port"])
        self.table_nodes.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_nodes.setStyleSheet("background-color: #313244; color: white;")
        main_layout.addWidget(self.table_nodes)

        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setStyleSheet("background-color: #181825; color: #f5e0dc;")
        main_layout.addWidget(self.log_console)

        self.setCentralWidget(central_widget)

        # Le Timer interroge uniquement le handler
        self.timer = QTimer()
        self.timer.timeout.connect(self.handler.on_update)
        self.timer.start(500)

    # --- MÉTHODES PASSIVES (Attendront les ordres du UIHandler) ---

    def refresh_status(self, c, r):
        """Mise à jour déclenchée par UIHandler.on_update"""
        self.label_stats.setText(f"STATUT : ACTIF | CLIENTS : {c} | ROUTEURS : {r}")

        # Le tableau est reconstruit selon les données fournies par le handler via le core
        self.table_nodes.setRowCount(0)
        for node in getattr(self.handler.core, 'list_routers', []):
            row = self.table_nodes.rowCount()
            self.table_nodes.insertRow(row)
            self.table_nodes.setItem(row, 0, QTableWidgetItem("Routeur"))
            self.table_nodes.setItem(row, 1, QTableWidgetItem(str(node.get('ip', 'N/A'))))
            self.table_nodes.setItem(row, 2, QTableWidgetItem(str(node.get('port', 'N/A'))))

        for node in getattr(self.handler.core, 'list_clients', []):
            row = self.table_nodes.rowCount()
            self.table_nodes.insertRow(row)
            self.table_nodes.setItem(row, 0, QTableWidgetItem("Client"))
            self.table_nodes.setItem(row, 1, QTableWidgetItem(str(node.get('ip', 'N/A'))))
            self.table_nodes.setItem(row, 2, QTableWidgetItem(str(node.get('port', 'N/A'))))

    def display_message(self, m):
        self.log_console.append(f"> {m}")

    def display_error(self, m):
        self.log_console.append(f"<span style='color:#f38ba8;'>ERR: {m}</span>")