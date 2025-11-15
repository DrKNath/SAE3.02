import socket
import threading
import time

class master:
    def __init__(self, host: str='0.0.0.0', port: int =0):
        self.__host = host
        self.__port = port
        self.__clients=[]
        self.__server_socket = socket.socket()
    
    def start(self):
        self.__server_socket.bind((self.__host, self.__port))
        self.__server_socket.listen(5)
        print(f"Serveur en écoute sur {self.__host}:{self.__port}")

        #Thread pour les nouvelles connexions
        self.__thread_client = threading.Thread(target=self.new_connection)
        self.__thread_client.daemon = True
        self.__thread_client.start()

        self.console()

        
    def console(self):
        while True:
            console_command = str(input("Console Serveur >> "))
            if console_command == '/stop':
                try:
                    self.__server.send("Le serveur va s'arrêter.".encode('utf-8'))
                    self.__server.close()
                except:
                    pass
                finally:
                    time.sleep(5)
                    self.__server_socket.close()
                    print("Serveur arrêté.")
                    break
    
    def new_connection(self):
        try:
            while True:
                client_socket, address = self.__server_socket.accept()
                self.__clients.append(client_socket)
                print(f"Connexion de {address}")

                #Thread Client 
                self.__thread_client = threading.Thread(target=self.broadcast , args=(client_socket, address))
                self.__thread_client.daemon = True
                self.__thread_client.start()
        except:
            print("Le serveur a été arrêté.")
        finally:
            self.__clients.remove(client_socket)
            client_socket.close()
            print(f"Déconnexion de {address}")


    def broadcast(self, client_socket, address, message_send=''):
        while True:
            message = self.__server.recv(1024).decode()
            if not message:
                break
            for client in self.__clients:
                if client != client_socket:
                    try: 
                        self.__server.send(message.encode('utf-8'))
                    except:
                        self.clients.remove(client)
            print(message)
        

if __name__ == "__main__":
    port = 10000
    server = master(port=port)
    server.start()




