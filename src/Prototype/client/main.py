from core.ClientCore import ClientCore
from core.UIHandler import UIHandler
from ui.terminal import TerminalUI

if __name__ == "__main__":
    name = input("Name >> ")
    port = int(input("Port >> "))

    # Création du core
    client_core = ClientCore(name=name, port=port)

    # Création du handler UI
    ui_handler = UIHandler(client_core)
    client_core.ui_handler = ui_handler  # référence du Core vers UIHandler

    # Terminal UI
    terminal_ui = TerminalUI(ui_handler)

    # Démarrage du client (threads master + réseau)
    client_core.start()

    # Démarrage de l'UI
    terminal_ui.start()
