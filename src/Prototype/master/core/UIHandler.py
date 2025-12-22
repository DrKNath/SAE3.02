class UIHandler:
    def __init__(self, core):
        self.core = core

    # événements core → UI
    def on_update(self):
        pass

    # getters UI
    def get_clients(self):
        return self.core.list_clients

    def get_routers(self):
        return self.core.list_routers

    def get_status(self):
        return {
            "clients": len(self.get_clients()),
            "routers": len(self.get_routers())
        }

    # actions UI → core
    def stop(self):
        self.core.stop()
