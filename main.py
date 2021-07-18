import cmdUI
import QtUI
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow

if __name__ == "__main__":
    # obj = cmdUI.cmdUI()
    # obj.entrance()
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = QtUI.Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

