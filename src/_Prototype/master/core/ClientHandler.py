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

                # Log historique et ajout à la table des nœuds actifs
                self.core.log_message_to_db("SYSTEM", name, f"Connexion Client: {ip}:{port}")
                self.core.db_manage_active_node(name, "CLIENT", ip, port)

                conn.send(self.serialize_lists().encode())

            elif ctype == "ROUTER":
                name, ip, port, pubkey = parts[1], parts[2], parts[3], parts[4]
                self.socket_routers.append(conn)
                self.core.list_routers.append({
                    "name": name, "ip": ip, "port": int(port), "public_key": pubkey
                })

                # [cite_start]Log historique et ajout à la table des nœuds actifs AVEC clé publique [cite: 126]
                self.core.log_message_to_db("SYSTEM", name, f"Connexion Routeur: {ip}:{port}")
                self.core.db_manage_active_node(name, "ROUTER", ip, port, pubkey)

        self.broadcast_to_clients()
        if hasattr(self.core, "ui_handler"):
            self.core.ui_handler.on_update()

    def disconnect(self, conn):
        node_name = None
        with self.core.lock:
            # Recherche du nom pour la suppression en BDD
            if conn in self.socket_clients:
                idx = self.socket_clients.index(conn)
                node_name = self.core.list_clients[idx]['name']
                self.socket_clients.remove(conn)
                del self.core.list_clients[idx]

            elif conn in self.socket_routers:
                idx = self.socket_routers.index(conn)
                node_name = self.core.list_routers[idx]['name']
                self.socket_routers.remove(conn)
                del self.core.list_routers[idx]

        # Suppression physique de la base de données
        if node_name:
            self.core.db_remove_active_node(node_name)

        self.broadcast_to_clients()
        if hasattr(self.core, "ui_handler"):
            self.core.ui_handler.on_update()

    def serialize_lists(self):
        clients_str = ";;".join(f"{c['name']}::{c['ip']}::{c['port']}" for c in self.core.list_clients)
        routers_str = ";;".join(f"{r['name']}::{r['ip']}::{r['port']}::{r['public_key']}" for r in self.core.list_routers)
        return f"CLIENTS:{clients_str}||ROUTERS:{routers_str}"

    def broadcast_to_clients(self):
        msg = self.serialize_lists().encode()
        for client in self.socket_clients[:]:
            try:
                client.send(msg)
            except:
                self.disconnect(client)

    def stop(self):
        for s in self.socket_clients + self.socket_routers:
            try:
                s.close()
            except: pass