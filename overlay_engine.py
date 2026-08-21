import sys
import os
import ctypes
from PyQt5.QtCore import Qt, QPoint, QTimer, pyqtSignal
from PyQt5.QtWidgets import QLabel, QMenu, QAction
from PyQt5.QtGui import QPixmap, QGuiApplication

class OverlayEngine(QLabel):
    # Signals for UI interactions
    pet_clicked = pyqtSignal()
    pet_drag_started = pyqtSignal()
    pet_drag_finished = pyqtSignal()
    context_menu_requested = pyqtSignal(QPoint)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Transparent Frameless Always-On-Top Top-Level Desktop Window
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Window
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setScaledContents(True)

        self.mascot_size = 150
        self.setFixedSize(self.mascot_size, self.mascot_size)

        # Dragging state tracking
        self.is_dragging = False
        self.drag_start_position = QPoint()
        self.click_start_pos = QPoint()

        # Gravity Simulation Variables
        self.is_falling = False
        self.velocity_y = 0.0
        self.gravity = 1.5
        self.bounce_factor = -0.3

        # Physics timer (30ms ~ 33 FPS)
        self.physics_timer = QTimer(self)
        self.physics_timer.timeout.connect(self._apply_gravity_step)
        self.physics_timer.start(30)

        # Position mascot right in the center of primary screen (500, 250)
        self.move(500, 250)

    def set_sprite(self, pixmap: QPixmap):
        if pixmap and not pixmap.isNull():
            scaled = pixmap.scaled(self.mascot_size, self.mascot_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(scaled)
            self.resize(self.mascot_size, self.mascot_size)

    def force_topmost(self):
        """Force HWND_TOPMOST via Windows Win32 API"""
        try:
            hwnd = int(self.winId())
            ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0040)
        except Exception as e:
            print(f"[OverlayEngine] Topmost error: {e}")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.is_falling = False
            self.velocity_y = 0.0
            self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            self.click_start_pos = event.globalPos()
            self.pet_drag_started.emit()
            event.accept()
        elif event.button() == Qt.RightButton:
            self.context_menu_requested.emit(event.globalPos())
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging and (event.buttons() & Qt.LeftButton):
            self.move(event.globalPos() - self.drag_start_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_dragging:
            self.is_dragging = False
            drag_distance = (event.globalPos() - self.click_start_pos).manhattanLength()
            if drag_distance < 5:
                self.pet_clicked.emit()
                self.pet_drag_finished.emit()
            else:
                self.is_falling = True
                self.velocity_y = 1.0
                self.pet_drag_finished.emit()
            event.accept()

    def _apply_gravity_step(self):
        try:
            if not self.is_falling or self.is_dragging:
                return

            pt = QPoint(int(self.x() + self.width() // 2), int(self.y() + self.height() // 2))
            screen = QGuiApplication.screenAt(pt)
            if not screen:
                screen = QGuiApplication.primaryScreen()
            if not screen:
                return

            geo = screen.availableGeometry()
            floor_y = geo.bottom() - self.height()

            current_y = self.y()

            if current_y < floor_y:
                self.velocity_y += self.gravity
                next_y = current_y + int(self.velocity_y)

                if next_y >= floor_y:
                    next_y = floor_y
                    if abs(self.velocity_y) > 4.0:
                        self.velocity_y *= self.bounce_factor
                    else:
                        self.velocity_y = 0.0
                        self.is_falling = False

                self.move(int(self.x()), int(next_y))
            else:
                self.move(int(self.x()), int(floor_y))
                self.velocity_y = 0.0
                self.is_falling = False
        except Exception as e:
            print(f"[OverlayEngine] Error in _apply_gravity_step: {e}")
