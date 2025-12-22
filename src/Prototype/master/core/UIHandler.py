class UIHandler:
    def __init__(self, core):
        """Initialise le pont entre la logique (core) et l'interface (ui)."""
        self.core = core
        self.ui = None  # Sera lié dynamiquement par MasterGUI

    def set_ui(self, ui):
        """Établit la connexion avec l'instance de MasterGUI."""
        self.ui = ui

    def handle_command(self, cmd):
        """Traite les commandes textuelles envoyées depuis l'interface."""
        parts = cmd.split()
        if not parts:
            return

        match parts:
            case ["/stop"]:
                self.core.stop()

            case ["/clients"]:
                if self.ui:
                    # Récupère la liste des clients du MasterCore
                    list_c = getattr(self.core, 'list_clients', [])
                    self.ui.display_clients(list_c)

            case ["/routers"]:
                if self.ui:
                    # Récupère la liste des routeurs du MasterCore
                    list_r = getattr(self.core, 'list_routers', [])
                    self.ui.display_routers(list_r)

            case _:
                if self.ui:
                    self.ui.display_error("Commande inconnue")

    def on_update(self):
        """
        Méthode de synchronisation appelée par le QTimer de l'IHM toutes les 500ms.
        C'est ici que le compteur passe de 0 à 1 dès qu'une connexion est détectée.
        """
        if self.ui and self.core:
            # Extraction sécurisée des longueurs de listes du MasterCore
            nb_clients = len(getattr(self.core, 'list_clients', []))
            nb_routers = len(getattr(self.core, 'list_routers', []))

            # Mise à jour des éléments visuels de MasterGUI
            self.ui.refresh_status(nb_clients, nb_routers)