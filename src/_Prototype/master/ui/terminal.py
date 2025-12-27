class TerminalUI:
    def __init__(self, ui_handler):
        self.ui_handler = ui_handler
        ui_handler.set_ui(self)

    def start(self):
        print("[INFO] Master Terminal UI démarrée")
        while self.ui_handler.core.running:
            try:
                cmd = input("master>> ").strip()
            except:
                break

            if cmd.startswith("/"):
                self.ui_handler.handle_command(cmd)

    def display_clients(self, clients):
        print("\n[CLIENTS]")
        for c in clients:
            print(c)

    def display_routers(self, routers):
        print("\n[ROUTERS]")
        for r in routers:
            print(r)

    def refresh_status(self, nb_clients, nb_routers):
        print(f"\n[STATUS] Clients={nb_clients} Routers={nb_routers}")

    def display_error(self, msg):
        print(f"[ERREUR] {msg}")
