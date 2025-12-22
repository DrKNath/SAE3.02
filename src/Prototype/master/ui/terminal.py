class TerminalUI:
    def __init__(self, ui_handler):
        self.ui = ui_handler
        self.running = True

    def start(self):
        while self.running:
            cmd = input("master> ").strip()

            if cmd == "clients":
                for c in self.ui.get_clients():
                    print(c)

            elif cmd == "routers":
                for r in self.ui.get_routers():
                    print(r)

            elif cmd == "status":
                print(self.ui.get_status())

            elif cmd == "exit":
                self.ui.stop()
                self.running = False

            else:
                print("clients | routers | status | exit")
