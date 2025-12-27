from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QHBoxLayout,
                             QLabel, QTextEdit, QLineEdit, QPushButton,
                             QListWidget, QGroupBox, QSpinBox)
from PyQt6.QtCore import QTimer, Qt

class ClientGUI(QMainWindow):
    def __init__(self, handler):
        super().__init__()
        self.handler = handler
        self.handler.set_ui(self)

        self.setWindowTitle("Client - Messagerie Oignon")
        self.resize(1100, 750)
        self.setStyleSheet("""
            QMainWindow { background-color: #f5f5f5; }
            QLabel { color: #333333; }
            QGroupBox { 
                font-weight: bold; 
                border: 2px solid #dddddd; 
                border-radius: 5px; 
                margin-top: 15px; 
                padding-top: 20px; 
                color: #333333; 
                background-color: #ffffff; 
            }
            QGroupBox::title { 
                subcontrol-origin: margin; 
                left: 10px; 
                padding: 0 3px; 
            }
        """)

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        top_layout = QHBoxLayout()


        left_panel = QVBoxLayout()
        id_box = QGroupBox("Mon Identité (Machine)")
        id_lay = QVBoxLayout()
        self.in_name = QLineEdit("Client_B")
        self.in_name.setStyleSheet("background-color: #ffffff; color: #333333; border: 1px solid #dddddd; border-radius: 4px; padding: 5px;")
        self.in_port = QLineEdit("20002")
        self.in_port.setStyleSheet("background-color: #ffffff; color: #333333; border: 1px solid #dddddd; border-radius: 4px; padding: 5px;")
        id_lay.addWidget(QLabel("Nom :")); id_lay.addWidget(self.in_name)
        id_lay.addWidget(QLabel("Port d'écoute :")); id_lay.addWidget(self.in_port)
        id_box.setLayout(id_lay)
        left_panel.addWidget(id_box)

        mst_box = QGroupBox("Connexion Master")
        mst_lay = QVBoxLayout()
        self.in_master_ip = QLineEdit("192.168.1.209")
        self.in_master_ip.setStyleSheet("background-color: #ffffff; color: #333333; border: 1px solid #dddddd; border-radius: 4px; padding: 5px;")
        self.in_master_port = QLineEdit("10001")
        self.in_master_port.setStyleSheet("background-color: #ffffff; color: #333333; border: 1px solid #dddddd; border-radius: 4px; padding: 5px;")
        self.btn_launch = QPushButton("🚀 Lancer le Client")
        self.btn_launch.setStyleSheet("background-color: #0d6efd; color: white; font-weight: bold; padding: 8px; border-radius: 4px;")
        self.btn_launch.clicked.connect(self.on_launch)
        mst_lay.addWidget(QLabel("IP Master :")); mst_lay.addWidget(self.in_master_ip)
        mst_lay.addWidget(QLabel("Port Master :")); mst_lay.addWidget(self.in_master_port)
        mst_lay.addWidget(self.btn_launch)
        mst_box.setLayout(mst_lay)
        left_panel.addWidget(mst_box)
        top_layout.addLayout(left_panel, 1)


        mid_panel = QVBoxLayout()
        mid_panel.addWidget(QLabel("Messages Reçus :"))
        self.receive_area = QTextEdit()
        self.receive_area.setReadOnly(True)
        self.receive_area.setStyleSheet("background-color: #1e1e1e; color: #ffffff; font-family: 'Consolas'; border: 1px solid #dddddd; border-radius: 4px; padding: 5px;")
        mid_panel.addWidget(self.receive_area, 3)

        send_box = QGroupBox("Envoi")
        send_lay = QVBoxLayout()
        self.msg_input = QTextEdit()
        self.msg_input.setMaximumHeight(80)
        self.msg_input.setStyleSheet("background-color: #1e1e1e; color: #ffffff; font-family: 'Consolas'; border: 1px solid #dddddd; border-radius: 4px; padding: 5px;")
        h_lay = QHBoxLayout()
        self.nb_hops = QSpinBox()
        self.nb_hops.setStyleSheet("background-color: #ffffff; color: #333333; border: 1px solid #dddddd; border-radius: 4px; padding: 5px;")
        self.nb_hops.setRange(1, 10); self.nb_hops.setValue(3)
        h_lay.addWidget(QLabel("Nombre de sauts :")); h_lay.addWidget(self.nb_hops)
        btn_send = QPushButton("✉ ENVOYER")
        btn_send.setStyleSheet("background-color: #198754; color: white; font-weight: bold; padding: 10px; border-radius: 4px;")
        btn_send.clicked.connect(self.on_send)
        send_lay.addWidget(self.msg_input); send_lay.addLayout(h_lay); send_lay.addWidget(btn_send)
        send_box.setLayout(send_lay)
        mid_panel.addWidget(send_box, 2)
        top_layout.addLayout(mid_panel, 2)


        right_panel = QVBoxLayout()
        self.list_c = QListWidget()
        self.list_r = QListWidget()
        self.list_c.setStyleSheet("background-color: #ffffff; color: #333333; border: 1px solid #dddddd; border-radius: 4px; padding: 5px;")
        self.list_r.setStyleSheet("background-color: #ffffff; color: #333333; border: 1px solid #dddddd; border-radius: 4px; padding: 5px;")
        right_panel.addWidget(QLabel("Clients (Destinataires) :")); right_panel.addWidget(self.list_c)
        right_panel.addWidget(QLabel("Routeurs actifs :")); right_panel.addWidget(self.list_r)
        top_layout.addLayout(right_panel, 1)

        main_layout.addLayout(top_layout, 4)
      
        main_layout.addWidget(QLabel("Logs du Client :"))
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setStyleSheet("background-color: #1e1e1e; color: #ffffff; font-family: 'Consolas';")
        self.log_console.setMaximumHeight(120)
        main_layout.addWidget(self.log_console)

        self.setCentralWidget(central_widget)
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_ui)
        self.timer.start(1000)

    def on_launch(self):
        self.handler.start_connection(self.in_master_ip.text(), self.in_master_port.text(),
                                      self.in_name.text(), self.in_port.text())

    def refresh_ui(self):
        """Met à jour les listes sans perdre la sélection"""
        selected_items = self.list_c.selectedItems()
        selected_text = selected_items[0].text() if selected_items else None

        self.list_c.clear()
        list_clients = self.handler.get_list_clients()
        for c in list_clients:
            client_display = f"{c['name']} @ {c['ip']}:{c['port']}"
            if c['name'] != self.handler.core.name:
                item = self.list_c.addItem(client_display)
                if client_display == selected_text:
                    self.list_c.setCurrentRow(self.list_c.count() - 1)

        self.list_r.clear()
        list_routers = self.handler.get_list_routers()
        for r in list_routers:
            self.list_r.addItem(f"Routeur: {r['name']}")

    def on_send(self):
        """Récupère l'élément sélectionné et envoie le message"""
        item = self.list_c.currentItem()
        if not item:
            self.log_message("⚠️ Veuillez sélectionner un destinataire dans la liste.")
            return

        try:
            # Extraction IP:Port depuis "Nom @ IP:Port"
            addr = item.text().split("@")[1].strip()
            ip, port = addr.split(":")
            msg = self.msg_input.toPlainText()

            if msg.strip():
                self.handler.send_message(msg, ip, port, self.nb_hops.value())
                self.receive_area.append(f"Moi : {msg}")
                self.msg_input.clear()
                self.log_message(f"✅ Message envoyé à {ip}:{port}")
        except Exception as e:
            self.log_message(f"❌ Erreur lors de l'envoi : {str(e)}")

    def display_message(self, m):
        self.receive_area.append(m)

    def log_message(self, m):
        self.log_console.append(f"> {m}")
