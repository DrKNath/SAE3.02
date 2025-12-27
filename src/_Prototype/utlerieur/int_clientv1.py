import sys
import time
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLineEdit, QTextEdit, QPushButton,
                             QLabel, QComboBox, QMessageBox)
from PyQt6.QtCore import (QThread, pyqtSignal, Qt)
import socket


class CipherSimulator:
    @staticmethod
    def encrypt_layer(data, key_id, next_hop_id, next_hop_addr):
        header = f"KEY:{key_id}|NEXT:{next_hop_id}|ADDR:{next_hop_addr}"
        encrypted_data = f"[[{header}|{data}]]_ENCRYPTED_WITH_{key_id}"
        return encrypted_data


class CommunicationThread(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, target_ip, target_port, payload):
        super().__init__()
        self.target_ip = target_ip
        self.target_port = target_port
        self.payload = payload

    def run(self):
        self.log_signal.emit(f"[COMM] Tentative de connexion à {self.target_ip}:{self.target_port}...")

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((self.target_ip, self.target_port))

                s.sendall(self.payload.encode('utf-8'))
                self.log_signal.emit("[COMM] Oignon envoyé avec succès au premier routeur.")

                self.finished_signal.emit(True, "Message transmis.")

        except socket.timeout:
            error_msg = f"Délai dépassé lors de la connexion/envoi à {self.target_ip}:{self.target_port}."
            self.log_signal.emit(f"[COMM ERROR] {error_msg}")
            self.finished_signal.emit(False, error_msg)

        except ConnectionRefusedError:
            error_msg = f"Connexion refusée par le routeur {self.target_ip}:{self.target_port}."
            self.log_signal.emit(f"[COMM ERROR] {error_msg}")
            self.finished_signal.emit(False, error_msg)

        except Exception as e:
            error_msg = f"Erreur inattendue lors de l'envoi : {e}"
            self.log_signal.emit(f"[COMM ERROR] {error_msg}")
            self.finished_signal.emit(False, error_msg)

        self.log_signal.emit("[COMM] Thread d'envoi terminé.")


class ClientWindow(QMainWindow):

    SIMULATED_TOPOLOGY = [
        {'id': 'R1', 'ip': '192.168.1.10', 'port': 5001, 'pub_key': 'PUB_R1_KEY_SIMULEE'},
        {'id': 'R2', 'ip': '192.168.1.11', 'port': 5002, 'pub_key': 'PUB_R2_KEY_SIMULEE'},
        {'id': 'R3', 'ip': '192.168.1.12', 'port': 5003, 'pub_key': 'PUB_R3_KEY_SIMULEE'},
        {'id': 'ClientB', 'ip': '192.168.1.21', 'port': 6002, 'pub_key': 'N/A'},
        {'id': 'ClientC', 'ip': '192.168.1.22', 'port': 6003, 'pub_key': 'N/A'},
    ]

    def __init__(self, client_id="ClientA"):
        super().__init__()
        self.client_id = client_id

        self.chat_history = []
        self.current_discussion_filter = "Global (Toutes discussions)"

        self.available_routers = [r for r in self.SIMULATED_TOPOLOGY if r['id'].startswith('R')]

        self.available_clients = [c for c in self.SIMULATED_TOPOLOGY if
                                  c['id'].startswith('Client') and c['id'] != self.client_id]

        all_clients = [c['id'] for c in self.SIMULATED_TOPOLOGY if c['id'].startswith('Client')]
        self.all_client_ids = sorted(list(set(all_clients + [client_id])))

        self.com_thread = None

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.setup_ui()
        self.update_client_display()
        self.update_discussion_combo()

    def setup_ui(self):
        self.setWindowTitle(f"Client Anonyme - Routeur Oignon")

        top_control_layout = QHBoxLayout()
        top_control_layout.addWidget(QLabel("<b>Nom du Client:</b>"))

        self.client_id_input = QLineEdit(self.client_id)
        self.client_id_input.setFixedWidth(100)
        top_control_layout.addWidget(self.client_id_input)

        self.set_client_btn = QPushButton("Changer Client ID")
        self.set_client_btn.clicked.connect(self.set_new_client_id)
        self.set_client_btn.setStyleSheet("background-color: #3498db; color: white;")
        top_control_layout.addWidget(self.set_client_btn)

        top_control_layout.addStretch(1)

        self.choose_route_btn = QPushButton("Choisir Route (TODO)")
        top_control_layout.addWidget(self.choose_route_btn)

        self.layout.addLayout(top_control_layout)

        discussion_layout = QHBoxLayout()
        discussion_layout.addWidget(QLabel("<b>Discussion :</b>"))
        self.discussion_combo = QComboBox()
        self.discussion_combo.setFixedWidth(200)
        self.discussion_combo.addItem("Global (Toutes discussions)")
        self.discussion_combo.currentIndexChanged.connect(self.update_chat_view)
        discussion_layout.addWidget(self.discussion_combo)
        discussion_layout.addWidget(QLabel("Choix de la discussion"))
        discussion_layout.addStretch(1)
        self.layout.addLayout(discussion_layout)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background-color: #333; color: #fff; font-size: 10pt; border: 1px solid #555;")
        self.layout.addWidget(self.chat_display)

        message_send_layout = QHBoxLayout()

        message_label = QLabel("MSG à ENVOYER")
        message_label.setStyleSheet("font-weight: bold;")
        message_send_layout.addWidget(message_label)

        self.message_input = QLineEdit()
        message_send_layout.addWidget(self.message_input)

        self.send_dest_combo = QComboBox()
        self.send_dest_combo.setFixedWidth(100)
        self._update_send_dest_combo()
        message_send_layout.addWidget(self.send_dest_combo)

        self.send_btn = QPushButton("Envoyer")
        self.send_btn.setStyleSheet("background-color: #007BFF; color: white; font-weight: bold;")
        self.send_btn.clicked.connect(self.send_message)
        message_send_layout.addWidget(self.send_btn)

        self.layout.addLayout(message_send_layout)

        self.layout.addWidget(QLabel("<b>LOGS (Journal Technique):</b>"))
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        self.log_widget.setMaximumHeight(150)
        self.log_widget.setStyleSheet("background-color: #222; color: #aaa; font-size: 8pt; border: 1px solid #444;")
        self.layout.addWidget(self.log_widget)

    def update_client_display(self):
        self.setWindowTitle(f"Client Anonyme - Routeur Oignon - Actif: {self.client_id}")

        self.available_clients = [c for c in self.SIMULATED_TOPOLOGY if
                                  c['id'].startswith('Client') and c['id'] != self.client_id]
        self.available_routers = [r for r in self.SIMULATED_TOPOLOGY if r['id'].startswith('R')]

        self._update_send_dest_combo()
        self.update_discussion_combo()
        self.update_chat_view()

    def set_new_client_id(self):
        new_id = self.client_id_input.text().strip()
        if new_id and new_id.startswith('Client') and len(new_id) >= 7:
            self.client_id = new_id
            self.log_message(f"[CTRL] Client ID changed to {self.client_id}.")
            self.update_client_display()
        else:
            QMessageBox.warning(self, "Erreur ID",
                                "L'ID doit commencer par 'Client' et avoir un suffixe (ex: ClientA, ClientB).")
            self.client_id_input.setText(self.client_id)

    def _update_send_dest_combo(self):
        self.send_dest_combo.clear()
        for client in self.available_clients:
            self.send_dest_combo.addItem(client['id'])

    def update_discussion_combo(self):
        self.discussion_combo.blockSignals(True)
        self.discussion_combo.clear()

        self.discussion_combo.addItem("Global (Toutes discussions)")

        for cid in self.all_client_ids:
            if cid != self.client_id:
                self.discussion_combo.addItem(cid)

        if self.current_discussion_filter not in [self.discussion_combo.itemText(i) for i in
                                                  range(self.discussion_combo.count())]:
            self.current_discussion_filter = "Global (Toutes discussions)"

        index = self.discussion_combo.findText(self.current_discussion_filter)
        if index != -1:
            self.discussion_combo.setCurrentIndex(index)

        self.discussion_combo.blockSignals(False)

    def update_chat_view(self):
        self.current_discussion_filter = self.discussion_combo.currentText()

        self.chat_display.clear()
        self.chat_display.append(f"--- Discussion: {self.current_discussion_filter} ---")

        filter_target = self.current_discussion_filter

        for msg in self.chat_history:
            is_global = filter_target == "Global (Toutes discussions)"

            is_relevant_to_current_client = (msg['sender'] == self.client_id) or (msg['recipient'] == self.client_id)

            is_sent_to_target = msg['sender'] == self.client_id and msg['recipient'] == filter_target
            is_received_from_target = msg['recipient'] == self.client_id and msg['sender'] == filter_target

            if is_relevant_to_current_client and (is_global or is_sent_to_target or is_received_from_target):

                if msg['sender'] == self.client_id:
                    display = f"<b style='color:#3498db;'>{msg['time']} [Moi -> {msg['recipient']}] :</b> {msg['message']}"
                elif msg['recipient'] == self.client_id:
                    display = f"<b style='color:#2ecc71;'>{msg['time']} [{msg['sender']} -> Moi] :</b> {msg['message']}"
                else:
                    display = f"<b style='color:#ccc;'>{msg['time']} [{msg['sender']} -> {msg['recipient']}] :</b> {msg['message']}"

                self.chat_display.append(display)

    def log_message(self, message):
        self.log_widget.append(f"[{time.strftime('%H:%M:%S')}] {message}")

    def select_circuit(self):
        try:
            circuit_length = 3
        except Exception:
            self.log_message("[ERROR] Circuit length must be an integer.")
            return None

        if circuit_length > len(self.available_routers):
            self.log_message("[ERROR] Requested circuit length is too large.")
            return None

        circuit = random.sample(self.available_routers, circuit_length)
        circuit_ids = " -> ".join([r['id'] for r in circuit])
        self.log_message(f"[CIRCUIT] {circuit_ids} selected (Length: {circuit_length})")
        self.log_message(f"[INFO] Circuit: {circuit_ids}")

        return circuit

    def create_onion(self, circuit, raw_message, destination_id, destination_addr):
        inner_data = f"DESTINATION:{destination_id}|MSG:{raw_message}"
        last_router = circuit[-1]
        last_pub_key = last_router['pub_key']

        current_payload = CipherSimulator.encrypt_layer(
            data=inner_data,
            key_id=last_pub_key,
            next_hop_id=destination_id,
            next_hop_addr=destination_addr
        )
        self.log_message(f"[CHIFF] Layer {len(circuit)} ({last_router['id']}): Encrypted for Destination.")

        for i in range(len(circuit) - 2, -1, -1):
            current_router = circuit[i]
            next_router = circuit[i + 1]

            next_hop_id = next_router['id']
            next_hop_addr = f"{next_router['ip']}:{next_router['port']}"
            current_pub_key = current_router['pub_key']

            current_payload = CipherSimulator.encrypt_layer(
                data=current_payload,
                key_id=current_pub_key,
                next_hop_id=next_hop_id,
                next_hop_addr=next_hop_addr
            )
            self.log_message(f"[CHIFF] Layer {i + 1} ({current_router['id']}): Encrypted for {next_router['id']}.")

        return current_payload

    def send_message(self):
        if self.com_thread and self.com_thread.isRunning():
            QMessageBox.warning(self, "Attention", "A message is already being sent. Please wait.")
            return

        dest_id = self.send_dest_combo.currentText()
        raw_message = self.message_input.text().strip()

        if not raw_message:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer un message à envoyer.")
            return

        dest_info = next((c for c in self.SIMULATED_TOPOLOGY if c['id'] == dest_id), None)
        dest_addr = f"{dest_info['ip']}:{dest_info['port']}"

        circuit = self.select_circuit()
        if not circuit:
            return

        self.log_message("[CHIFF] --- Starting Onion Encryption ---")
        full_onion_payload = self.create_onion(
            circuit=circuit,
            raw_message=raw_message,
            destination_id=dest_id,
            destination_addr=dest_addr
        )
        self.log_message("[CHIFF] FULL Onion created.")

        first_hop = circuit[0]
        self.log_message(f"[ENVOI] Sending to first hop ({first_hop['id']}) : {first_hop['ip']}:{first_hop['port']}")

        self.send_btn.setEnabled(False)

        self.add_to_chat_history(self.client_id, dest_id, raw_message)
        self.message_input.clear()

        self.com_thread = CommunicationThread(
            target_ip=first_hop['ip'],
            target_port=first_hop['port'],
            payload=full_onion_payload
        )
        self.com_thread.log_signal.connect(self.log_message)
        self.com_thread.finished_signal.connect(self.on_send_finished)
        self.com_thread.start()

    def on_send_finished(self, success, message):
        self.log_message(f"[RESPONSE] Transmission ended. Statut: {'SUCCESS' if success else 'FAILURE'} ({message})")
        self.send_btn.setEnabled(True)

    def add_to_chat_history(self, sender, recipient, message):
        current_time = time.strftime('%H:%M:%S')

        self.chat_history.append({
            'sender': sender,
            'recipient': recipient,
            'message': message,
            'time': current_time
        })
        self.update_chat_view()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    client_a_gui = ClientWindow(client_id="ClientA")
    client_a_gui.show()

    client_b_gui = ClientWindow(client_id="ClientB")
    client_b_gui.move(client_a_gui.x() + client_a_gui.width() + 20, client_a_gui.y())
    client_b_gui.show()

    client_a_gui.add_to_chat_history("ClientB", "ClientA", "Salut Client A, on teste le réseau ?")
    client_a_gui.add_to_chat_history("ClientA", "ClientB", "Oui, ça fonctionne même si c'est simulé.")
    client_a_gui.add_to_chat_history("ClientC", "ClientA", "Test depuis C vers A.")

    client_b_gui.add_to_chat_history("ClientB", "ClientA", "Salut Client A, on teste le réseau ?")
    client_b_gui.add_to_chat_history("ClientA", "ClientB", "Oui, ça fonctionne même si c'est simulé.")
    client_b_gui.add_to_chat_history("ClientC", "ClientB", "Message secret pour B.")

    sys.exit(app.exec())
