import sys
from PyQt6.QtWidgets import QApplication
from .core.ClientCore import ClientCore
from .core.UIHandler import UIHandler
from .ui.Int_Client import ClientGUI

def main():

    client_core = ClientCore(name="Temp", port=0)
    ui_handler = UIHandler(client_core)
    client_core.ui_handler = ui_handler

    app = QApplication(sys.argv)
    gui = ClientGUI(ui_handler)
    gui.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
