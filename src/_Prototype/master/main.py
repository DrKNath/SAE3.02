import sys
from PyQt6.QtWidgets import QApplication
from .core.MasterCore import MasterCore
from .core.UIHandler import UIHandler
from .ui.Int_Master import MasterGUI


def main():
    # Initialisation sans port (sera défini par l'UI)
    core = MasterCore()
    handler = UIHandler(core)

    app = QApplication(sys.argv)
    gui = MasterGUI(handler)
    gui.show()

    # Le core.start() n'est plus appelé ici, mais par le bouton dans la GUI
    sys.exit(app.exec())


if __name__ == "__main__":
    main()