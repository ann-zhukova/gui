import sys
from pathlib import Path

from PyQt6.QtCore import QTimer, Qt, pyqtSlot
from PyQt6.QtGui import QFont, QKeyEvent, QMouseEvent, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel,
    QMessageBox, QPushButton, QVBoxLayout, QWidget,
)

ASSETS = Path(__file__).resolve().parent / "assets"


class Lab1Window(QWidget):
    """Окно с двумя действиями из задания ЛР 1."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ЛР 1")
        self.setMinimumSize(680, 560)
        self.resize(760, 620)
        self.shaped = False
        self.image_visible = False
        self.drag_offset = None
        self.picture = QPixmap(str(ASSETS / "landscape.png"))
        self.skin = QPixmap(str(ASSETS / "window_skin.png"))
        if self.picture.isNull() or self.skin.isNull():
            raise RuntimeError("Не найдены PNG в папке assets. Восстановите файлы программы.")

        root = QVBoxLayout(self)
        root.setContentsMargins(36, 36, 36, 36)
        self.card = QFrame()
        self.card.setObjectName("card")
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(34, 30, 34, 30)
        card_layout.setSpacing(16)

        title = QLabel("Лабораторная работа № 1")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle = QLabel("Надпись, изображение и форма окна")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)

        self.content = QLabel("Нажмите кнопку, чтобы заменить эту надпись изображением")
        self.content.setObjectName("content")
        self.content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content.setWordWrap(True)
        self.content.setMinimumHeight(250)
        card_layout.addWidget(self.content, 1)

        actions = QHBoxLayout()
        actions.setSpacing(14)
        self.image_button = QPushButton("Показать изображение")
        self.image_button.clicked.connect(self.toggle_image)
        self.shape_button = QPushButton("Изменить форму окна")
        self.shape_button.setObjectName("secondaryButton")
        self.shape_button.clicked.connect(self.toggle_shape)
        actions.addWidget(self.image_button)
        actions.addWidget(self.shape_button)
        card_layout.addLayout(actions)
        self.close_button = QPushButton("Закрыть")
        self.close_button.setObjectName("secondaryButton")
        self.close_button.clicked.connect(self.close)
        card_layout.addWidget(self.close_button)
        root.addWidget(self.card)

        # Эффект нельзя назначать карточке с интерактивными дочерними
        # виджетами: на Windows Qt кэширует их до первого resizeEvent.
        shadow = QGraphicsDropShadowEffect(title)
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 3)
        shadow.setColor(Qt.GlobalColor.black)
        title.setGraphicsEffect(shadow)

        self.setStyleSheet("""
            QWidget { background-color: #1e1e2e; color: #ffffff;
                font-family: "Segoe UI"; font-size: 10pt; }
            QFrame#card { background-color: #252538; border: 1px solid #35354d;
                border-radius: 16px; }
            QLabel { background: transparent; }
            QLabel#title { color: #ffffff; font-size: 18pt; font-weight: 700; }
            QLabel#subtitle { color: #aaa7c2; font-size: 10pt; }
            QLabel#content { background-color: #1a1a28; border: 1px solid #35354d;
                border-radius: 12px; color: #d9d7e8; padding: 16px; }
            QPushButton { min-height: 24px; padding: 12px 18px; border: none;
                border-radius: 8px; background-color: #7c4dff; color: #ffffff;
                font-weight: 600; }
            QPushButton:hover { background-color: #8f69ff; }
            QPushButton:pressed { background-color: #6838e6; }
            QPushButton:focus { border: 2px solid #b69cff; padding: 10px 16px; }
            QPushButton#secondaryButton { background-color: #34344b;
                border: 1px solid #4b4b68; }
            QPushButton#secondaryButton:hover { background-color: #44445f; }
        """)

    @pyqtSlot()
    def toggle_image(self) -> None:
        self.image_visible = not self.image_visible
        if self.image_visible:
            self.content.setPixmap(self.picture.scaled(
                max(1, self.content.width() - 32), max(1, self.content.height() - 32),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ))
            self.image_button.setText("Вернуть надпись")
        else:
            self.content.clear()
            self.content.setText("Нажмите кнопку, чтобы заменить эту надпись изображением")
            self.image_button.setText("Показать изображение")

    @pyqtSlot()
    def toggle_shape(self) -> None:
        """Применяет альфа-маску PNG и возвращает обычную геометрию."""
        self.shaped = not self.shaped
        if self.shaped:
            self._apply_skin_mask()
            self.shape_button.setText("Вернуть обычную форму")
        else:
            self.clearMask()
            self.shape_button.setText("Изменить форму окна")

    def _apply_skin_mask(self) -> None:
        mask = self.skin.scaled(
            self.size(), Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        ).mask()
        self.setMask(mask)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self.shaped:
            self._apply_skin_mask()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if self.shaped and event.button() == Qt.MouseButton.LeftButton:
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.drag_offset = None
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            return
        super().keyPressEvent(event)


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))
    try:
        window = Lab1Window()
    except RuntimeError as exc:
        QMessageBox.critical(None, "Ошибка загрузки изображений", str(exc))
        return 1
    window.show()
    QTimer.singleShot(0, lambda: refresh_initial_geometry(window))
    return app.exec()


def refresh_initial_geometry(window: QWidget) -> None:
    """Завершает layout после создания нативного окна без смены геометрии."""
    window.ensurePolished()
    if window.layout() is not None:
        window.layout().invalidate()
        window.layout().activate()
    for widget in window.findChildren(QWidget):
        widget.ensurePolished()
        widget.updateGeometry()
    window.update()


if __name__ == "__main__":
    sys.exit(main())
