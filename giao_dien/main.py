import sys

from PyQt5.QtWidgets import QApplication

from app import AppTro

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppTro()
    window.show()
    sys.exit(app.exec_())