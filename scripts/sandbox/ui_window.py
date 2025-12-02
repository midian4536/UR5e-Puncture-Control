from PyQt5.QtWidgets import QApplication
from ui.ui_main_window import UIMainWindow

app = QApplication([])
ui = UIMainWindow()
ui.show()
app.exec_()
