import sys

from data import Database
from PyQt5.QtWidgets import QApplication
from ui import MainWindow

if __name__ == "__main__":
    with Database("/FlightDBv2.db") as db:
        app = QApplication(sys.argv)
        window = MainWindow(database=db)
        window.show()
        sys.exit(app.exec_())
