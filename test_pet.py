import sys
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QPixmap, QGuiApplication

class TestPet(QLabel):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        pixmap = QPixmap("assets/sprites/idle_1.png")
        self.setPixmap(pixmap)
        self.resize(pixmap.size())
        
        # Position in center of screen
        screen = QGuiApplication.primaryScreen()
        geo = screen.geometry()
        self.move(geo.x() + 400, geo.y() + 300)
        self.show()
        print(f"TestPet is showing at {self.pos()} on screen {geo}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = TestPet()
    # Close after 3 seconds for test
    QTimer.singleShot(3000, app.quit)
    sys.exit(app.exec_())
