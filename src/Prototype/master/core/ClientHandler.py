class ClientHandler:
    def __init__(self, core):
        self.core = core

        self.socket_clients = []
        self.socket_routers = []

    def handle(self, conn, msg):
        parts = msg.split("::")
        ctype = parts[0]

        with self.core.lock:
            if ctype == "CLIENT":
                name, ip, port = parts[1], parts[2], parts[3]
                self.socket_clients.append(conn)
                self.core.list_clients.append({"name": name, "ip": ip, "port": int(port)})

                # ON VÉRIFIE SI LA BDD EST PRÊTE AVANT D'ÉCRIRE
                if getattr(self.core, 'db_connected', False):
                    self.core.log_message_to_db("SYSTEM", name, f"Connexion Client: {ip}:{port}")

                conn.send(self.serialize_lists().encode())

            elif ctype == "ROUTER":
                name, ip, port, pubkey = parts[1], parts[2], parts[3], parts[4]
                self.socket_routers.append(conn)
                self.core.list_routers.append({
                    "name": name, "ip": ip, "port": int(port), "public_key": pubkey
                })

                # ON VÉRIFIE SI LA BDD EST PRÊTE
                if getattr(self.core, 'db_connected', False):
                    self.core.log_message_to_db("SYSTEM", name, f"Connexion Routeur: {ip}:{port}")

        self.broadcast_to_clients()

        if hasattr(self.core, "ui_handler"):
            self.core.ui_handler.on_update()

    def serialize_lists(self):
        clients_str = ";;".join(
            f"{c['name']}::{c['ip']}::{c['port']}"
            for c in self.core.list_clients
        )

        routers_str = ";;".join(
            f"{r['name']}::{r['ip']}::{r['port']}::{r['public_key']}"
            for r in self.core.list_routers
        )

        return f"CLIENTS:{clients_str}||ROUTERS:{routers_str}"

    def broadcast_to_clients(self):
        msg = self.serialize_lists().encode()

        for client in self.socket_clients[:]:
            try:
                client.send(msg)
            except:
                self.disconnect(client)

    def disconnect(self, conn):
        with self.core.lock:
            if conn in self.socket_clients:
                idx = self.socket_clients.index(conn)
                self.socket_clients.remove(conn)
                del self.core.list_clients[idx]

            if conn in self.socket_routers:
                idx = self.socket_routers.index(conn)
                self.socket_routers.remove(conn)
                del self.core.list_routers[idx]

        self.broadcast_to_clients()

        if hasattr(self.core, "ui_handler"):
            self.core.ui_handler.on_update()

    def stop(self):
        for s in self.socket_clients + self.socket_routers:
            try:
                s.close()
            except:
                pass
