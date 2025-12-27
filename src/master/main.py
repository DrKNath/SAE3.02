import sys
from PyQt6.QtWidgets import QApplication
from .core.MasterCore import MasterCore
from .core.UIHandler import UIHandler
from .ui.Int_Master import MasterGUI


def main():
    core = MasterCore()
    handler = UIHandler(core)

    app = QApplication(sys.argv)
    gui = MasterGUI(handler)
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
