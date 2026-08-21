import sys
import os
import random
from enum import Enum
from PyQt5.QtCore import QObject, QTimer, pyqtSignal, Qt, QPoint
from PyQt5.QtGui import QPixmap, QGuiApplication

class PetState(Enum):
    IDLE = "IDLE"
    WALK_LEFT = "WALK_LEFT"
    WALK_RIGHT = "WALK_RIGHT"
    DRAGGED = "DRAGGED"
    CLICKED = "CLICKED"

class AnimationEngine(QObject):
    # Signals to notify overlay window of frame or position updates
    frame_changed = pyqtSignal(QPixmap)
    position_delta = pyqtSignal(int, int) # dx, dy

    def __init__(self, sprites_dir=None, parent=None):
        super().__init__(parent)
        if sprites_dir is None:
            if getattr(sys, 'frozen', False):
                app_dir = os.path.dirname(sys.executable)
            else:
                app_dir = os.path.dirname(os.path.abspath(__file__))
            
            external_sprites = os.path.join(app_dir, "assets", "sprites")
            if os.path.exists(external_sprites):
                sprites_dir = external_sprites
            elif getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                sprites_dir = os.path.join(getattr(sys, '_MEIPASS'), "assets", "sprites")
            else:
                sprites_dir = external_sprites
        self.sprites_dir = sprites_dir

        self.current_state = PetState.IDLE
        self.state_timer = 0
        self.walk_speed = 3 # pixels per tick
        self.current_frame_index = 0
        self.clicked_ticks = 0

        # Load sprites mapping
        self.sprites = {
            PetState.IDLE: [],
            PetState.WALK_LEFT: [],
            PetState.WALK_RIGHT: [],
            PetState.DRAGGED: [],
            PetState.CLICKED: []
        }
        self.load_sprites()

        # Update timer (30ms interval)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_loop)
        self.timer.start(30)

    def load_sprites(self):
        self.sprites = {
            PetState.IDLE: [],
            PetState.WALK_LEFT: [],
            PetState.WALK_RIGHT: [],
            PetState.DRAGGED: [],
            PetState.CLICKED: []
        }
        def load_pixmap(filename):
            path = os.path.join(self.sprites_dir, filename)
            if os.path.exists(path):
                return QPixmap(path)
            print(f"[AnimationEngine] Sprite file missing: {path}")
            return None

        # IDLE frames
        f1 = load_pixmap("idle_1.png")
        f2 = load_pixmap("idle_2.png")
        if f1: self.sprites[PetState.IDLE].append(f1)
        if f2: self.sprites[PetState.IDLE].append(f2)

        # WALK LEFT frames
        wl1 = load_pixmap("walk_l1.png")
        wl2 = load_pixmap("walk_l2.png")
        if wl1: self.sprites[PetState.WALK_LEFT].append(wl1)
        if wl2: self.sprites[PetState.WALK_LEFT].append(wl2)

        # WALK RIGHT frames
        wr1 = load_pixmap("walk_r1.png")
        wr2 = load_pixmap("walk_r2.png")
        if wr1: self.sprites[PetState.WALK_RIGHT].append(wr1)
        if wr2: self.sprites[PetState.WALK_RIGHT].append(wr2)

        # DRAGGED & CLICKED
        drag = load_pixmap("dragged.png")
        if drag: self.sprites[PetState.DRAGGED].append(drag)

        clk = load_pixmap("clicked.png")
        if clk: self.sprites[PetState.CLICKED].append(clk)

    def set_state(self, new_state: PetState):
        if self.current_state != new_state:
            self.current_state = new_state
            self.current_frame_index = 0
            self.state_timer = 0
            if new_state == PetState.CLICKED:
                self.clicked_ticks = 25 # Display clicked pose for ~750ms

    def trigger_click(self):
        self.set_state(PetState.CLICKED)

    def trigger_drag(self):
        self.set_state(PetState.DRAGGED)

    def release_drag(self):
        self.set_state(PetState.IDLE)

    def update_bounds_check(self, window_x, window_width, window_y=0):
        try:
            pt = QPoint(int(window_x + window_width // 2), int(window_y + 64))
            screen = QGuiApplication.screenAt(pt)
            if not screen:
                screen = QGuiApplication.primaryScreen()
            if not screen:
                return
            geo = screen.availableGeometry()

            # Touch left edge
            if window_x <= geo.left() and self.current_state == PetState.WALK_LEFT:
                self.set_state(PetState.WALK_RIGHT)

            # Touch right edge
            elif window_x + window_width >= geo.right() and self.current_state == PetState.WALK_RIGHT:
                self.set_state(PetState.WALK_LEFT)
        except Exception as e:
            print(f"[AnimationEngine] Error in update_bounds_check: {e}")

    def _update_loop(self):
        frames = self.sprites.get(self.current_state, [])
        if frames:
            # Animate frame (change frame every 6 ticks ~180ms)
            if self.state_timer % 6 == 0:
                self.current_frame_index = (self.current_frame_index + 1) % len(frames)
                pixmap = frames[self.current_frame_index]
                self.frame_changed.emit(pixmap)

        dx = 0
        dy = 0

        # Handle CLICKED state reset
        if self.current_state == PetState.CLICKED:
            self.clicked_ticks -= 1
            if self.clicked_ticks <= 0:
                self.set_state(PetState.IDLE)

        # Handle Walking logic
        elif self.current_state == PetState.WALK_LEFT:
            dx = -self.walk_speed
        elif self.current_state == PetState.WALK_RIGHT:
            dx = self.walk_speed

        # Random State Decision (switch state every ~3-6 seconds)
        if self.current_state not in [PetState.DRAGGED, PetState.CLICKED]:
            if self.state_timer > random.randint(100, 200):
                self.state_timer = 0
                next_action = random.choice([PetState.IDLE, PetState.WALK_LEFT, PetState.WALK_RIGHT])
                self.set_state(next_action)

        self.state_timer += 1
        if dx != 0 or dy != 0:
            self.position_delta.emit(dx, dy)
