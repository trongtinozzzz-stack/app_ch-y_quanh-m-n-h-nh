import sys
import os
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QApplication, QMenu, QAction, QFileDialog, QMessageBox

import traceback

def exception_hook(exctype, value, tb):
    print("Unhandled Exception:", exctype, value)
    traceback.print_tb(tb)
    sys.__excepthook__(exctype, value, tb)

sys.excepthook = exception_hook

from overlay_engine import OverlayEngine
from animation_engine import AnimationEngine, PetState
from audio_manager import AudioManager
from ai_generator import AIGeneratorThread

class DesktopPetApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        # Initialize core managers
        self.audio_manager = AudioManager()
        self.animation_engine = AnimationEngine()
        self.overlay_window = OverlayEngine()

        self._connect_signals()
        
        # Trigger initial frame display
        initial_frames = self.animation_engine.sprites.get(PetState.IDLE, [])
        if initial_frames:
            self.overlay_window.set_sprite(initial_frames[0])
            
        self.overlay_window.show()
        self.overlay_window.raise_()
        self.overlay_window.activateWindow()
        self.overlay_window.force_topmost()

    def _connect_signals(self):
        # Frame animation -> Overlay sprite updates
        self.animation_engine.frame_changed.connect(self.overlay_window.set_sprite)

        # Movement delta -> Overlay movement & Screen bounds check
        self.animation_engine.position_delta.connect(self._handle_position_delta)

        # Mascot mouse interactions
        self.overlay_window.pet_clicked.connect(self._handle_pet_click)
        self.overlay_window.pet_drag_started.connect(self.animation_engine.trigger_drag)
        self.overlay_window.pet_drag_finished.connect(self.animation_engine.release_drag)
        self.overlay_window.context_menu_requested.connect(self._show_context_menu)

    def _handle_position_delta(self, dx, dy):
        if not self.overlay_window.is_dragging and not self.overlay_window.is_falling:
            new_x = self.overlay_window.x() + dx
            new_y = self.overlay_window.y() + dy
            self.overlay_window.move(new_x, new_y)
            self.animation_engine.update_bounds_check(new_x, self.overlay_window.width(), new_y)

    def _handle_pet_click(self):
        self.audio_manager.play_random_sound()
        self.animation_engine.trigger_click()

    def _show_context_menu(self, global_pos: QPoint):
        menu = QMenu(self.overlay_window)
        
        # Style Context Menu
        menu.setStyleSheet("""
            QMenu {
                background-color: #2b2b36;
                color: #ffffff;
                border: 1px solid #444454;
                border-radius: 8px;
                padding: 4px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #ff6b81;
                color: #ffffff;
            }
        """)

        # Option 1: AI Face-to-Chibi conversion with Gemini
        ai_action = QAction("✨ Đổi mặt bạn nữ (Gemini AI)", menu)
        ai_action.triggered.connect(self._open_ai_gen_dialog)
        menu.addAction(ai_action)

        # Option 2: Restore Default Anya
        reset_action = QAction("🔄 Khôi phục Anya mặc định", menu)
        reset_action.triggered.connect(self._restore_default_anya)
        menu.addAction(reset_action)

        # Option 3: Sound Toggle
        sound_status = "Bật" if self.audio_manager.sound_enabled else "Tắt"
        sound_action = QAction(f"🔊 Âm thanh: {sound_status}", menu)
        sound_action.triggered.connect(self._toggle_sound)
        menu.addAction(sound_action)

        menu.addSeparator()

        # Option 4: Quit
        exit_action = QAction("❌ Thoát", menu)
        exit_action.triggered.connect(self._quit_app)
        menu.addAction(exit_action)

        menu.exec_(global_pos)

    def _toggle_sound(self):
        is_enabled = self.audio_manager.toggle_sound()
        print(f"[DesktopPetApp] Sound toggled: {is_enabled}")

    def _open_ai_gen_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.overlay_window,
            "Chọn ảnh bạn nữ để ghép mặt Chibi AI",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if file_path:
            print(f"[DesktopPetApp] Selected image for AI conversion: {file_path}")
            self.ai_thread = AIGeneratorThread(file_path)
            self.ai_thread.finished_signal.connect(self._on_ai_gen_finished)
            self.ai_thread.start()

    def _on_ai_gen_finished(self, success, result):
        if success:
            print("[DesktopPetApp] AI Mascot generated successfully! Reloading sprites...")
            self.animation_engine.load_sprites()
            frames = self.animation_engine.sprites.get(PetState.IDLE, [])
            if frames:
                self.overlay_window.set_sprite(frames[0])
            QMessageBox.information(
                self.overlay_window,
                "Thành công",
                "Đã dùng Gemini AI quét khuôn mặt bạn nữ và tạo Desktop Pet mới thành công!"
            )
        else:
            QMessageBox.warning(
                self.overlay_window,
                "Lỗi AI Gen",
                f"Không thể tạo Mascot từ ảnh: {result}"
            )

    def _restore_default_anya(self):
        try:
            import process_anya_sprites
            self.animation_engine.load_sprites()
            frames = self.animation_engine.sprites.get(PetState.IDLE, [])
            if frames:
                self.overlay_window.set_sprite(frames[0])
            QMessageBox.information(
                self.overlay_window,
                "Khôi phục thành công",
                "Đã đặt lại nhân vật bé Anya mặc định!"
            )
        except Exception as e:
            QMessageBox.warning(self.overlay_window, "Lỗi", f"Không thể khôi phục: {e}")

    def _quit_app(self):
        self.app.quit()

    def run(self):
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    pet_app = DesktopPetApp()
    pet_app.run()
