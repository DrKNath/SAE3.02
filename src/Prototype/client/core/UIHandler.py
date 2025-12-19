class UIHandler:
    def __init__(self, core):
        self.core = core
        self.ui = None  # TerminalUI ou GUI

    def set_ui(self, ui):
        self.ui = ui

    def send_message(self, message):
        route = self.core.onion_router.gen_route()
        self.core.route = route
        onion = self.core.onion_router.build_onion(message, route, '192.0.0.2', 30002)
        self.core.network_handler.send_to_first_router(onion)

    def handle_command(self, cmd):
        parts = cmd.split()
        match parts:
            case ["/ip", "master", ip]:
                self.core.master_conn.master_host = ip
                if self.ui: self.ui.update_master_ip_field(ip)
            case ["/port", "master", port]:
                self.core.master_conn.master_port = int(port)
                if self.ui: self.ui.update_master_port_field(port)
            case _:
                print("[ERREUR] Commande inconnue")

    def notify_received_message(self, msg):
        if self.ui:
            self.ui.display_message(msg)
