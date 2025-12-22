from .core.MasterCore import MasterCore
from .core.UIHandler import UIHandler
from .ui.terminal import TerminalUI

if __name__ == "__main__":
    port = int(input("Port >> "))

    master_core = MasterCore(port=port)

    ui_handler = UIHandler(master_core)
    master_core.ui_handler = ui_handler

    terminal_ui = TerminalUI(ui_handler)

    master_core.start()
    terminal_ui.start()
