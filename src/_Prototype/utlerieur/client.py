import socket
import threading

class Client:
    def __init__(self, host: str ='', port: int =0):
        self.__host = host
        self.__port = port
        self.__socket = socket.socket()
        client_socket = socket.socket()

    def connect(self):
        self.__socket.connect((self.__host, self.__port))
        print("Connecté au serveur!")

        # Thread pour recevoir les messages
        thread_receive = threading.Thread(target=self.receive_message)
        thread_receive.daemon = True
        thread_receive.start()

        #Thread pour envoyer les messages
        self.send_message()


    def send_message(self):
        while True:
            try:
                message = str(input(">> "))
                if message == '/quit':
                    break
                self.__socket.send(message.encode('utf-8'))
            except:
                print("Impossible d'envoyer le message. Vous êtes peut-être déconnecté.")
                break
        self.__socket.close()


    def receive_message(self):
        while True:
            try :
                reply = self.__socket.recv(1024).decode()
                if not reply:
                    break
                print(f"\nMessage reçu: {reply}\n>> ", end='')
            except:
                print("Vous avez été déconnecté du serveur.")
                break





if __name__ == "__main__":
    host = '192.0.0.2'
    port = 10000
    client = Client(host, port)
    client.connect()


