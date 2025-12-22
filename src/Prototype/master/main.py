import sys
from PyQt6.QtWidgets import QApplication


from .core.MasterCore import MasterCore
from .core.UIHandler import UIHandler
from .ui.Int_Master import MasterGUI


def main():
    port = int(input("Port >> "))
    core = MasterCore(port=port)
    handler = UIHandler(core)
    core.handler=handler

    app = QApplication(sys.argv)


    gui = MasterGUI(handler)
    gui.show()


    core.start()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()