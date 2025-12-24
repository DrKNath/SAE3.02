class UIHandler:
    def __init__(self, core):
        self.core = core
        self.ui = None

    def set_ui(self, ui):
        self.ui = ui

    def request_shutdown(self):
        self.core.shutdown_network()

    def start_master(self, port_str):
        """Récupère le port de l'UI et lance le Core"""
        try:
            port = int(port_str)
            self.core.port = port
            self.core.start()
            if self.ui:
                self.ui.display_message(f"Serveur démarré sur le port {port}")
                self.ui.btn_start.setEnabled(False)
                self.ui.port_input.setEnabled(False)
        except ValueError:
            if self.ui:
                self.ui.display_message("ERREUR : Port invalide")

    def on_update(self):
        # On récupère les données du core sans le modifier
        nb_cl = len(self.core.list_clients)
        nb_ro = len(self.core.list_routers)
        db_st = "Connectée" if self.core.db_connected else "Déconnectée"

        # On pousse vers la GUI
        self.ui.refresh_status(nb_cl, nb_ro)
        self.ui.update_statistics(nb_cl, nb_ro, db_st)
        self.ui.refresh_keys()