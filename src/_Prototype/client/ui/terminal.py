class TerminalUI:
    def __init__(self, ui_handler):
        self.ui_handler = ui_handler
        self.master_ip_field = ""
        self.master_port_field = ""
        ui_handler.set_ui(self)

    def start(self):
        print("[INFO] Terminal UI démarrée")
        while self.ui_handler.core.running:
            try:
                message = input(">> ").strip()
            except:
                break

            if message.startswith("/"):
                self.ui_handler.handle_command(message)
            else:
                self.ui_handler.send_message(message)

    def display_message(self, msg):
        print(f"\n[MSG REÇU] {msg}\n>> ", end="")

    def update_master_ip_field(self, ip):
        self.master_ip_field = ip

    def update_master_port_field(self, port):
        self.master_port_field = port
