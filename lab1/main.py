import os
import sys
from pathlib import Path

from PyQt5 import QtCore


plugins = Path(QtCore.__file__).resolve().parent / "Qt5" / "plugins"
if (plugins / "platforms").is_dir():
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(plugins)
    QtCore.QCoreApplication.addLibraryPath(str(plugins))

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QPainter, QPixmap, QRegion
from PyQt5.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QMessageBox, QPushButton,
    QVBoxLayout, QWidget,
)

ASSETS = Path(__file__).resolve().parent / "assets"


class Lab1Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ЛР 1 - Надпись и изображение")
        self.setFixedSize(680, 480)
        self.shaped = False
        self.image_visible = False
        self.drag_offset = None
        self.picture = QPixmap(str(ASSETS / "landscape.png"))
        self.skin = QPixmap(str(ASSETS / "window_skin.png"))
        if self.picture.isNull() or self.skin.isNull():
            raise RuntimeError("Не найдены PNG в папке assets. Восстановите файлы программы.")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(62, 42, 62, 48)
        title = QLabel("Лабораторная работа № 1")
        title.setAlignment(Qt.AlignCenter)
        title.setAttribute(Qt.WA_TransparentForMouseEvents)
        layout.addWidget(title)
        self.content = QLabel("Нажмите кнопку, чтобы заменить эту надпись изображением")
        self.content.setAlignment(Qt.AlignCenter)
        self.content.setWordWrap(True)
        self.content.setMinimumHeight(240)
        layout.addWidget(self.content, 1)
        buttons = QHBoxLayout()
        self.image_button = QPushButton("Показать изображение")
        self.image_button.clicked.connect(self.toggle_image)
        buttons.addWidget(self.image_button)
        layout.addLayout(buttons)
        self.close_button = QPushButton("Закрыть")
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.close_button, alignment=Qt.AlignCenter)
        self.setStyleSheet(
            "QLabel { color: #18324d; font-size: 16px; background: transparent; }"
            "QPushButton { background: #225aa5; color: white; padding: 10px;"
            "border: none; border-radius: 6px; font-size: 13px; }"
            "QPushButton:hover { background: #3474c4; }"
            "QPushButton:focus { border: 2px solid #e6a400; }"
        )

    @pyqtSlot()
    def toggle_image(self):
        self.image_visible = not self.image_visible
        if self.image_visible:
            self.content.setPixmap(self.picture.scaled(
                440, 240, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
            self.image_button.setText("Вернуть надпись")
        else:
            self.content.setText("Нажмите кнопку, чтобы заменить эту надпись изображением")
            self.image_button.setText("Показать изображение")

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.shaped:
            painter.drawPixmap(self.rect(), self.skin)
        else:
            painter.fillRect(self.rect(), Qt.white)

    def mousePressEvent(self, event):
        if self.shaped and event.button() == Qt.LeftButton:
            self.drag_offset = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drag_offset is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.drag_offset)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.drag_offset = None
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)


def main():
    app = QApplication(sys.argv)
    try:
        window = Lab1Window()
    except RuntimeError as exc:
        QMessageBox.critical(None, "Ошибка загрузки изображений", str(exc))
        return 1
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
