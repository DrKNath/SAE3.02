class UIHandler:
    def __init__(self, core):
        self.core = core

    def start(self):
        while True:
            message = input(">> ").strip()
            if message.startswith("/"):
                self.handle_command(message)
            else:
                onion = self.core.onion_router.build_onion(message)
                if onion:
                    self.core.network_handler.send_to_first_router(onion)

    def handle_command(self, cmd):
        parts = cmd.split()
        match parts:
            case ["/ip", "master", ip]:
                self.core.master_conn.master_host = ip
                print(f"[INFO] Master IP défini: {ip}")
            case ["/port", "master", port]:
                self.core.master_conn.master_port = int(port)
                print(f"[INFO] Master port défini: {port}")
            case _:
                print("[ERREUR] Commande inconnue.")
