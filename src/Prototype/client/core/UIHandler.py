class UIHandler:
    def __init__(self, core):
        self.core = core
        self.ui = None

    def set_ui(self, ui):
        self.ui = ui

    def get_list_clients(self):
        """Récupère les clients sans toucher au Core"""
        return self.core.list_clients

    def get_list_routers(self):
        """Récupère les routeurs sans toucher au Core"""
        return self.core.list_routers

    def send_message(self, message, dest_ip, dest_port, nb_hops):
        """Envoie le message avec la destination choisie dans l'interface"""
        route = self.core.onion_router.gen_route(nb_hops)
        self.core.route = route
        onion = self.core.onion_router.build_onion(self.core.name + ' : ' +  message, route, dest_ip, int(dest_port))
        self.core.network_handler.send_to_first_router(onion)

    def start_connection(self, master_ip, master_port, client_name, client_port):
        """Configure le client et lance les threads du Core"""
        self.core.name = client_name
        self.core.port = int(client_port)
        self.core.master_conn.master_host = master_ip
        self.core.master_conn.master_port = int(master_port)
        self.core.start()

    def notify_received_message(self, msg):
        if self.ui:
            self.ui.display_message(msg)