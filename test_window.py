import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QPixmap

app = QApplication(sys.argv)
lbl = QLabel()
lbl.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Window)
lbl.setAttribute(Qt.WA_TranslucentBackground, True)
pm = QPixmap("assets/sprites/idle_1.png").scaled(160, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
lbl.setPixmap(pm)
lbl.resize(160, 160)
lbl.move(550, 300)
lbl.show()
lbl.raise_()
lbl.activateWindow()

print("Showing window at:", lbl.pos(), "Size:", lbl.size(), "Visible:", lbl.isVisible())

# Keep open for 5 seconds
QTimer.singleShot(5000, app.quit)
app.exec_()
