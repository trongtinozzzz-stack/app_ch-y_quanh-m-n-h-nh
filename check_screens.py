import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QGuiApplication

app = QApplication(sys.argv)
for i, screen in enumerate(QGuiApplication.screens()):
    print(f"Screen {i}: name={screen.name()}, geometry={screen.geometry()}, availableGeometry={screen.availableGeometry()}")
