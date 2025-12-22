class UIHandler:
    def __init__(self, core):
        self.core = core
        self.ui = None

    def set_ui(self, ui):
        self.ui = ui

    def handle_command(self, cmd):
        parts = cmd.split()

        match parts:
            case ["/stop"]:
                self.core.stop()

            case ["/clients"]:
                if self.ui:
                    self.ui.display_clients(self.core.list_clients)

            case ["/routers"]:
                if self.ui:
                    self.ui.display_routers(self.core.list_routers)

            case _:
                if self.ui:
                    self.ui.display_error("Commande inconnue")
    
    def on_update(self):
        if self.ui:
            self.ui.refresh_status(
                len(self.core.list_clients),
                len(self.core.list_routers)
            )
    
    def stop_master(self):
        self.core.stop()

    def set_master_port(self, port: int):
        self.core.port = port
        # éventuellement redémarrer le socket
        if self.ui:
            self.ui.refresh_status(len(self.core.list_clients), len(self.core.list_routers))

    def refresh_ui(self):
        if self.ui:
            self.ui.refresh_status(len(self.core.list_clients), len(self.core.list_routers))
