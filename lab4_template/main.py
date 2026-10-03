import sys
from datetime import datetime
from pathlib import Path
from time import monotonic

from PyQt6.QtCore import QObject, QTimer, QUrl, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine


class Interface(QObject):
    """По таймеру запрашивает у QML сохранение холста в PNG."""

    saveRequested = pyqtSignal(str)
    saved = pyqtSignal(str)
    saveFailed = pyqtSignal(str)
    statusChanged = pyqtSignal(str)

    def __init__(self, save_directory: Path | None = None) -> None:
        super().__init__()
        self.save_directory = save_directory or Path(__file__).resolve().parent
        self.save_directory.mkdir(parents=True, exist_ok=True)
        self.interval_ms = 10_000
        self.timer = QTimer(self)
        self.timer.setInterval(self.interval_ms)
        self.timer.timeout.connect(self.request_save)
        self.last_saved_path = ""
        self._started = False
        self._last_request_at = 0.0

    @pyqtSlot()
    def start(self) -> None:
        if self._started:
            return
        self._started = True
        self.timer.start()
        self.statusChanged.emit(
            f"Автосохранение включено: {self.save_directory}"
        )
        # Первое сохранение выполняется вскоре после показа окна, когда Canvas
        # уже получил размеры и успел отрисовать фон.
        QTimer.singleShot(1_000, self.request_save)

    @pyqtSlot()
    def stop(self) -> None:
        self.timer.stop()
        self._started = False

    @pyqtSlot()
    def request_save(self) -> None:
        # Микросекунды исключают перезапись при ручном и автоматическом
        # сохранении в пределах одной секунды.
        requested_at = monotonic()
        if requested_at - self._last_request_at < 0.25:
            return
        self._last_request_at = requested_at
        try:
            self.save_directory.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            message = f"Не удалось создать каталог {self.save_directory}: {exc}"
            self.saveFailed.emit(message)
            print(message, file=sys.stderr)
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        path = self.save_directory / f"painting_{timestamp}.png"
        self.statusChanged.emit(f"Сохранение: {path}")
        self.saveRequested.emit(str(path))

    @pyqtSlot(str, bool)
    def save_completed(self, path: str, success: bool) -> None:
        if success:
            self.last_saved_path = path
            self.saved.emit(path)
            print(f"Рисунок сохранён: {path}")
        else:
            message = f"Не удалось сохранить файл: {path}"
            self.saveFailed.emit(message)
            print(message, file=sys.stderr)


def main() -> int:
    app = QGuiApplication(sys.argv)
    try:
        interface = Interface()
    except OSError as exc:
        print(f"Ошибка создания каталога для рисунков: {exc}", file=sys.stderr)
        return 1

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("_backend", interface)
    qml_file = Path(__file__).resolve().parent / "mainWindow.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    if not engine.rootObjects():
        print(f"Ошибка: не удалось загрузить QML-файл {qml_file}", file=sys.stderr)
        return 1
    interface.start()
    app.aboutToQuit.connect(interface.stop)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
