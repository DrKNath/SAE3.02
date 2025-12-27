import socket
import threading
import time
import re

class Master: 
    def __init__(self, host: str ='0.0.0.0', port: int =0):
        self.__host = host
        self.__port = port
        self.__server_socket = socket.socket()
        self.__list_clients = []
        self.__list_routers = []


        print(f"Serveur démarré sur {self.__host}:{self.__port}")
    
    
    def start(self):
        self.__server_socket.bind((self.__host, self.__port))
        self.__server_socket.listen(5)
        print(f"Serveur en écoute sur {self.__host}:{self.__port}")
        #Thread pour les nouvelles connexions
        thread_connection = threading.Thread(target=self.new_connection)
        thread_connection.daemon = True
        thread_connection.start()


        #Thread pour la console serveur
        self.console()

    def console(self):
        while True: 
            command = str(input("Console Serveur >> "))
            if command == '/stop':
                try:
                    self.broadcast("Le serveur va s'arrêter.", None)
                    self.deconnected_all_client()
                except:
                    pass
                finally:
                    time.sleep(1)
                    self.__server_socket.close()
                    print("Serveur arrêté.")
                    break
            if command == '/list':
                self.print_clients()
    
    def new_connection(self):
        try:
            while True:
                conn, address = self.__server_socket.accept()
                print(f"Connexion de {address}\n>> ", end='')
                self.__clients.append(conn)

                #Thread pour chaque nouveau Client
                thread_client = threading.Thread(target=self.connected_clients, args=(conn, address))
                thread_client.daemon = True
                thread_client.start()
        except:
            print("Le serveur a été arrêté.")
    
    def deconnected_all_client(self):
        for client in self.__clients:
            try: 
                client.close()
            except: pass
            self.__clients.remove(client)
            print(f"Le client {client} est déconnecté.")

    def rcv_msg(self, client_socket, address):
        try:
            message = client_socket.recv(1024).decode('utf-8')
            self.decrypt_msg(message)
        except:
            pass
    
    def decrypt_msg(self, msg):
        pattern = r'^(CLIENT|ROUTER)::([^:]+)::([^:]+)::([^:]+)(?:::(.*))?$'
        match = re.match(pattern, msg)
        if match:
            if match.group(1) == 'CLIENT':
                self.__list_clients.append({
                    'name': match.group(2),
                    'ip': match.group(3),
                    'port': int(match.group(4))
                })

            if match.group(1) == 'ROUTER':
                self.__list_routers.append({
                    'name': match.group(2),
                    'ip': match.group(3),
                    'port': int(match.group(4)),
                    'public_key': match.group(5)
                })  
    
    def broadcast(self, message, sender_socket):
        for client in self.__clients:
            if client != sender_socket:
                try:
                    client.send(message.encode('utf-8'))
                except:
                    self.__clients.remove(client)
    

    def print_clients(self):
        print("Clients connectés:")
        for client in self.__clients:
            print(client.getpeername())
    
    


if __name__ == "__main__":
    port = 10000
    server = Master(port=port)
    server.start()