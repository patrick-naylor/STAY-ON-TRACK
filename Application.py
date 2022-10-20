# Written by Patrick Naylor
from PyQt5.QtWidgets import QApplication, QLabel
app = QApplication([])
label = QLabel('Hello World!')
label.show()
app.exec()