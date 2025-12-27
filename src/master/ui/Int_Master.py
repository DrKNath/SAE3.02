from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QHBoxLayout,
                             QLabel, QTextEdit, QTableWidget, QTableWidgetItem,
                             QHeaderView, QPushButton, QTabWidget, QGroupBox, QLineEdit)
from PyQt6.QtCore import QTimer, Qt


class MasterGUI(QMainWindow):
    def __init__(self, handler):
        super().__init__()
        self.handler = handler
        self.handler.set_ui(self)

        self.setWindowTitle("Master - Routage en Oignon")
        self.resize(1000, 750)
        self.setStyleSheet("""
            QMainWindow { background-color: #f5f5f5; }
            QLabel { color: #333333; }
            QTabWidget::pane { border: 1px solid #dddddd; background-color: #ffffff; }
            QTabBar::tab { background-color: #e9ecef; color: #333333; padding: 8px 16px; border: 1px solid #dddddd; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; }
            QTabBar::tab:selected { background-color: #ffffff; font-weight: bold; }
        """)

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)

        header_layout.addWidget(QLabel("Port :"))
        self.port_input = QLineEdit()
        self.port_input.setText("10001")
        self.port_input.setFixedWidth(80)
        header_layout.addWidget(self.port_input)

        self.btn_start = QPushButton("🚀 Démarrer")
        self.btn_start.setStyleSheet(
            "padding: 8px; background-color: #0d6efd; color: white; font-weight: bold; border-radius: 4px;")
        self.btn_start.clicked.connect(self.on_start_clicked)
        header_layout.addWidget(self.btn_start)

        header_layout.addStretch()

        self.label_routers = QLabel("Routeurs : 0")
        self.label_routers.setStyleSheet(
            "font-size: 13px; color: #ffffff; padding: 10px 15px; background-color: #0d6efd; border-radius: 4px; font-weight: bold;")
        header_layout.addWidget(self.label_routers)

        self.label_clients = QLabel("Clients : 0")
        self.label_clients.setStyleSheet(
            "font-size: 13px; color: #ffffff; padding: 10px 15px; background-color: #198754; border-radius: 4px; font-weight: bold;")
        header_layout.addWidget(self.label_clients)

        main_layout.addWidget(header_widget)

        self.btn_shutdown = QPushButton("🛑 Arrêt Total")
        self.btn_shutdown.setStyleSheet(
            "padding: 10px; background-color: #dc3545; color: white; font-weight: bold; border-radius: 4px;")
        self.btn_shutdown.clicked.connect(self.on_shutdown_clicked)
        main_layout.addWidget(self.btn_shutdown)

        self.tabs = QTabWidget()

        tab_nodes = QWidget()
        nodes_layout = QVBoxLayout(tab_nodes)
        nodes_layout.setContentsMargins(15, 15, 15, 15)
        nodes_layout.addWidget(QLabel("Nœuds connectés au réseau"))
        self.table_nodes = QTableWidget(0, 5)
        self.table_nodes.setHorizontalHeaderLabels(["Type", "ID/Nom", "Adresse IP", "Port", "État"])
        self.table_nodes.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        nodes_layout.addWidget(self.table_nodes)
        self.tabs.addTab(tab_nodes, "📡 Nœuds")

        tab_keys = QWidget()
        keys_layout = QVBoxLayout(tab_keys)
        keys_layout.setContentsMargins(15, 15, 15, 15)
        keys_layout.addWidget(QLabel("Clés publiques des routeurs"))
        self.table_keys = QTableWidget(0, 3)
        self.table_keys.setHorizontalHeaderLabels(["Routeur", "Clé publique", "État"])
        self.table_keys.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        keys_layout.addWidget(self.table_keys)
        self.tabs.addTab(tab_keys, "🔑 Clés")

        tab_stats = QWidget()
        stats_layout = QVBoxLayout(tab_stats)
        stats_layout.setContentsMargins(15, 15, 15, 15)
        stats_layout.addWidget(QLabel("Statistiques du réseau"))

        stats_grid = QWidget()
        stats_grid_layout = QHBoxLayout(stats_grid)

        cl_cont = QVBoxLayout()
        cl_cont.addWidget(QLabel("<b>Nombre de Clients</b>")) 
        group_clients = QGroupBox("Statut")
        group_clients.setStyleSheet("font-weight: bold; border: 2px solid #dddddd; border-radius: 5px;")
        cl_lay = QVBoxLayout(group_clients)
        self.label_messages = QLabel("Total : 0")
        self.label_messages.setStyleSheet("font-size: 24px; color: #0d6efd; font-weight: bold;")
        self.label_messages.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl_lay.addWidget(self.label_messages)
        cl_cont.addWidget(group_clients)
        stats_grid_layout.addLayout(cl_cont)

        ro_cont = QVBoxLayout()
        ro_cont.addWidget(QLabel("<b>Nombre de Routeurs</b>"))  
        group_routers = QGroupBox("Statut")
        group_routers.setStyleSheet("font-weight: bold; border: 2px solid #dddddd; border-radius: 5px;")
        ro_lay = QVBoxLayout(group_routers)
        self.label_routes = QLabel("Total : 0")
        self.label_routes.setStyleSheet("font-size: 24px; color: #198754; font-weight: bold;")
        self.label_routes.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ro_lay.addWidget(self.label_routes)
        ro_cont.addWidget(group_routers)
        stats_grid_layout.addLayout(ro_cont)

        db_cont = QVBoxLayout()
        db_cont.addWidget(QLabel("<b>Base de Données</b>"))  
        group_db = QGroupBox("État")
        group_db.setStyleSheet("font-weight: bold; border: 2px solid #dddddd; border-radius: 5px;")
        db_lay = QVBoxLayout(group_db)
        self.label_db = QLabel("Déconnectée")
        self.label_db.setStyleSheet("font-size: 24px; color: #dc3545; font-weight: bold;")
        self.label_db.setAlignment(Qt.AlignmentFlag.AlignCenter)
        db_lay.addWidget(self.label_db)
        db_cont.addWidget(group_db)
        stats_grid_layout.addLayout(db_cont)

        stats_layout.addWidget(stats_grid)
        stats_layout.addStretch()
        self.tabs.addTab(tab_stats, "📊 Statistiques")

        main_layout.addWidget(self.tabs)

        main_layout.addWidget(QLabel("Logs du système"))
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setMaximumHeight(180)
        self.log_console.setStyleSheet("background-color: #1e1e1e; color: #ffffff; font-family: 'Consolas';")
        main_layout.addWidget(self.log_console)

        self.setCentralWidget(central_widget)

        self.timer = QTimer()
        self.timer.timeout.connect(self.handler.on_update)
        self.timer.start(500)

    def refresh_status(self, num_clients, num_routers):
        self.label_routers.setText(f"Routeurs : {num_routers}")
        self.label_clients.setText(f"Clients : {num_clients}")
        self.table_nodes.setRowCount(0)

        for node in getattr(self.handler.core, 'list_routers', []):
            row = self.table_nodes.rowCount()
            self.table_nodes.insertRow(row)
            self.table_nodes.setItem(row, 0, QTableWidgetItem("Routeur"))
            self.table_nodes.setItem(row, 1, QTableWidgetItem(str(node.get('name', 'N/A'))))
            self.table_nodes.setItem(row, 2, QTableWidgetItem(str(node.get('ip', 'N/A'))))
            self.table_nodes.setItem(row, 3, QTableWidgetItem(str(node.get('port', 'N/A'))))
            status_item = QTableWidgetItem("Actif")
            status_item.setForeground(Qt.GlobalColor.darkGreen)
            self.table_nodes.setItem(row, 4, status_item)

        for node in getattr(self.handler.core, 'list_clients', []):
            row = self.table_nodes.rowCount()
            self.table_nodes.insertRow(row)
            self.table_nodes.setItem(row, 0, QTableWidgetItem("Client"))
            self.table_nodes.setItem(row, 1, QTableWidgetItem(str(node.get('name', 'N/A'))))
            self.table_nodes.setItem(row, 2, QTableWidgetItem(str(node.get('ip', 'N/A'))))
            self.table_nodes.setItem(row, 3, QTableWidgetItem(str(node.get('port', 'N/A'))))
            status_item = QTableWidgetItem("Actif")
            status_item.setForeground(Qt.GlobalColor.darkGreen)
            self.table_nodes.setItem(row, 4, status_item)

    def update_statistics(self, clients, routers, db_status):
        self.label_messages.setText(f"Total : {clients}")
        self.label_routes.setText(f"Total : {routers}")

        self.label_db.setText(db_status)
        if db_status == "Connectée":
            self.label_db.setStyleSheet("font-size: 24px; color: #198754; font-weight: bold;")
        else:
            self.label_db.setStyleSheet("font-size: 24px; color: #dc3545; font-weight: bold;")

    def refresh_keys(self):
        self.table_keys.setRowCount(0)
        for node in getattr(self.handler.core, 'list_routers', []):
            row = self.table_keys.rowCount()
            self.table_keys.insertRow(row)
            self.table_keys.setItem(row, 0, QTableWidgetItem(str(node.get('name', 'N/A'))))
            self.table_keys.setItem(row, 1, QTableWidgetItem(str(node.get('public_key', 'N/A'))))
            status_item = QTableWidgetItem("Active")
            status_item.setForeground(Qt.GlobalColor.darkGreen)
            self.table_keys.setItem(row, 2, status_item)

    def on_start_clicked(self):
        port_val = self.port_input.text()
        self.handler.start_master(port_val)

    def on_shutdown_clicked(self):
        self.handler.request_shutdown()
        self.close()

    def display_message(self, m):
        self.log_console.append(f"> {m}")
