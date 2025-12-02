from PyQt5.QtWidgets import QApplication
from ui.ui_main_window import UIMainWindow
from ui.ui_controller import UIController


def main():
    app = QApplication([])
    ui = UIMainWindow()
    controller = UIController(ui, config_path="configs/robot.yaml")
    ui.show()
    app.exec_()


if __name__ == "__main__":
    main()
