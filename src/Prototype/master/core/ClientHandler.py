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

            elif ctype == "ROUTER":
                self.socket_routers.append(conn)
                self.core.list_routers.append({
                    "name": parts[1],
                    "ip": parts[2],
                    "port": int(parts[3]),
                    "public_key": parts[4]
                })

        # notifier UI
        if hasattr(self.core, "ui_handler"):
            self.core.ui_handler.on_update()

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

        if hasattr(self.core, "ui_handler"):
            self.core.ui_handler.on_update()

    def stop(self):
        for s in self.socket_clients + self.socket_routers:
            try:
                s.close()
            except:
                pass
