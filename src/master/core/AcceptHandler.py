import socket
import threading

class AcceptHandler:
    def __init__(self, core):
        self.core = core

        self.server_socket = socket.socket()
        self.server_socket.bind((core.host, core.port))
        self.server_socket.listen(5)

    def start_server(self):
        while self.core.running:
            conn, addr = self.server_socket.accept()

            threading.Thread(
                target=self.handle_client,
                args=(conn, addr),
                daemon=True
            ).start()

    def handle_client(self, conn, addr):
        while self.core.running:
            try:
                msg = conn.recv(1024).decode()
                if not msg:
                    break

                self.core.client_handler.handle(conn, msg)

            except:
                break

        self.core.client_handler.disconnect(conn)
        conn.close()

    def stop(self):
        self.server_socket.close()
