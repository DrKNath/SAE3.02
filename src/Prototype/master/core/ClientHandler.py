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
                self.socket_clients.append(conn)
                self.core.list_clients.append({
                    "name": parts[1],
                    "ip": parts[2],
                    "port": int(parts[3])
                })

                conn.send(self.serialize_lists().encode())

            elif ctype == "ROUTER":
                self.socket_routers.append(conn)
                self.core.list_routers.append({
                    "name": parts[1],
                    "ip": parts[2],
                    "port": int(parts[3]),
                    "public_key": parts[4]
                })

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
