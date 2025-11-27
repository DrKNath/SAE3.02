import socket
import threading
import time

class Master: 
    def __init__(self, host: str ='0.0.0.0', port: int =0):
        self.__host = host
        self.__port = port

        self.__server_socket = socket.socket()
        self.__server_socket.bind((self.__host, self.__port))
        self.__server_socket.listen(5)

        self.__socket_clients = []
        self.__socket_routers = []

        self.__list_clients = []
        self.__list_routers = []

    def start(self):
        try: 
            while True: 
                conn, add = self.__server_socket.accept()
                thread = threading.Thread(target=self.rcv_msg, args=(conn, add))
                thread.daemon = True
                thread.start()
        except:     
            self.stop()


    def rcv_msg(self, client_socket, address):
        try:
            while True: 
                message = client_socket.recv(1024).decode('utf-8')
                
                if not message:
                    print(f"[DC] Déconnexion détectée: {address}")
                    self.remove_socket(client_socket)
                    break
                
                c_type = self.decrypt_msg(message)


                if c_type == 'CLIENT':
                    self.__socket_clients.append(client_socket)
                    print(f"Client connecté: {address}")
                    client_socket.send(self.serialize_lists().encode('utf-8'))

                elif c_type == 'ROUTER':
                    self.__socket_routers.append(client_socket)
                    print(f"Router connecté: {address}")
                
                # broadcast uniquement aux clients
                self.broadcast_lists_to_clients()

        except Exception as e:
            print(f"[ERR] Problème avec {address}: {e}")
            self.remove_socket(client_socket)
    
    def decrypt_msg(self, msg):
        part = msg.split("::")
        c_type = part[0]
        if c_type == "CLIENT":
            name, ip, port = part[1], part[2], part[3]
            self.__list_clients.append({
                'name': name,
                'ip': ip,
                'port': int(port)
            })
    
        elif c_type == "ROUTER":
            name, ip, port, public_key = part[1], part[2], part[3], part[4]
            self.__list_routers.append({
                'name': name,
                'ip': ip,
                'port': int(port),
                'public_key': public_key
            })
        return c_type


    # Envoie au client
    def serialize_lists(self):
        clients_str = ";;".join(
            f"{c['name']}::{c['ip']}::{c['port']}"
            for c in self.__list_clients
        )
        routers_str = ";;".join(
            f"{r['name']}::{r['ip']}::{r['port']}::{r['public_key']}"
            for r in self.__list_routers
        )
        return f"CLIENTS:{clients_str}||ROUTERS:{routers_str}"
    
    def broadcast_lists_to_clients(self):
        msg = self.serialize_lists()
        for client in self.__socket_clients:
            try:
                print("aa")
                client.send(msg.encode('utf-8'))
            except:
                print("a")
                self.remove_socket(client)

    def remove_socket(self, client_socket):
        removed = False
        print("dd")
        if client_socket in self.__socket_clients:
            print("ddd")
            index = self.__socket_clients.index(client_socket)
            self.__socket_clients.remove(client_socket)
            del self.__list_clients[index]
            removed = True
        if client_socket in self.__socket_routers:
            index = self.__socket_routers.index(client_socket)
            self.__socket_routers.remove(client_socket)
            del self.__list_routers[index]
            removed = True
        if removed:
            try:
                print("dddd")
                client_socket.close()
            except:
                pass
            print("[TCP] Listes mises à jour après déconnexion")
            self.broadcast_lists_to_clients()


    def stop(self):
        for client in self.__socket_clients:
            try: 
                client.close()
            except: pass
            print(f"Le client {client} est déconnecté.")
        
        for client in self.__socket_routers:
            try: 
                client.close()
            except: pass
            print(f"Le router {client} est déconnecté.")



if __name__ == "__main__":
    master_server = Master(port=10001)
    master_server.start()
