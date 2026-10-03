import sys

from PyQt6.QtCore import QLocale, QSignalBlocker, QTimer, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication, QDoubleSpinBox, QFormLayout, QGraphicsDropShadowEffect,
    QGroupBox, QLabel, QPushButton, QVBoxLayout, QWidget,
)

if __package__:
    from .cl2 import CurrencyModel
    from .currency import MAX_AMOUNT, MAX_RATE, MIN_RATE
else:
    from cl2 import CurrencyModel
    from currency import MAX_AMOUNT, MAX_RATE, MIN_RATE


class ConverterWindow(QWidget):
    amount_edited = pyqtSignal(str, float)
    rates_edited = pyqtSignal(float, float)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ЛР 2")
        self.setMinimumSize(640, 660)
        self.resize(700, 700)
        self.model = CurrencyModel(self)
        root = QVBoxLayout(self)
        root.setContentsMargins(34, 30, 34, 30)
        root.setSpacing(18)

        title = QLabel("Конвертер валют")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        intro = QLabel("Измените любую сумму — остальные валюты пересчитаются автоматически")
        intro.setObjectName("subtitle")
        intro.setAlignment(Qt.AlignmentFlag.AlignCenter)
        intro.setWordWrap(True)
        root.addWidget(title)
        root.addWidget(intro)

        amounts = QGroupBox("Суммы")
        amounts.setObjectName("card")
        form = QFormLayout(amounts)
        form.setContentsMargins(24, 26, 24, 22)
        form.setHorizontalSpacing(24)
        form.setVerticalSpacing(16)
        self.fields: dict[str, QDoubleSpinBox] = {}
        for code, label in (
            ("RUB", "Рубли (RUB)"), ("USD", "Доллары (USD)"), ("EUR", "Евро (EUR)"),
        ):
            field = self.make_spinbox(2, 0, float(MAX_AMOUNT))
            field.setObjectName(code)
            field.setAccessibleName(label)
            field.valueChanged.connect(
                lambda value, currency=code: self.amount_edited.emit(currency, value)
            )
            self.fields[code] = field
            form.addRow(label, field)
        root.addWidget(amounts)

        rates = QGroupBox("Учебные курсы")
        rates.setObjectName("card")
        rate_form = QFormLayout(rates)
        rate_form.setContentsMargins(24, 26, 24, 22)
        rate_form.setHorizontalSpacing(24)
        rate_form.setVerticalSpacing(16)
        self.usd_rate = self.make_spinbox(4, float(MIN_RATE), float(MAX_RATE))
        self.eur_rate = self.make_spinbox(4, float(MIN_RATE), float(MAX_RATE))
        self.usd_rate.setSuffix(" ₽ / USD")
        self.eur_rate.setSuffix(" ₽ / EUR")
        rate_form.addRow("Курс доллара", self.usd_rate)
        rate_form.addRow("Курс евро", self.eur_rate)
        self.usd_rate.valueChanged.connect(self.publish_rates)
        self.eur_rate.valueChanged.connect(self.publish_rates)
        root.addWidget(rates)

        shadow = QGraphicsDropShadowEffect(title)
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 3)
        shadow.setColor(Qt.GlobalColor.black)
        title.setGraphicsEffect(shadow)

        self.status = QLabel()
        self.status.setObjectName("status")
        self.status.setWordWrap(True)
        root.addWidget(self.status)
        close_button = QPushButton("Закрыть")
        close_button.setObjectName("secondaryButton")
        close_button.clicked.connect(self.close)
        root.addWidget(close_button)

        self.amount_edited.connect(self.model.set_amount)
        self.rates_edited.connect(self.model.set_rates)
        self.model.amounts_changed.connect(self.show_amounts)
        self.model.error_occurred.connect(self.show_error)
        self.setStyleSheet("""
            QWidget { background-color: #1e1e2e; color: #ffffff;
                font-family: "Segoe UI"; font-size: 10pt; }
            QLabel { background: transparent; }
            QLabel#title { font-size: 19pt; font-weight: 700; }
            QLabel#subtitle { color: #aaa7c2; margin-bottom: 4px; }
            QGroupBox#card { background-color: #252538; border: 1px solid #393950;
                border-radius: 12px; margin-top: 14px; padding-top: 8px; font-weight: 600; }
            QGroupBox#card::title { subcontrol-origin: margin; left: 18px;
                padding: 0 8px; color: #b69cff; }
            QDoubleSpinBox { min-height: 24px; min-width: 280px; padding: 9px 12px;
                background-color: #191927; color: #ffffff; border: 1px solid #45455f;
                border-radius: 8px; selection-background-color: #7c4dff; }
            QDoubleSpinBox:focus { border: 2px solid #7c4dff; padding: 8px 11px; }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 22px; background: #34344b; border: none; }
            QLabel#status { background-color: #252538; border-radius: 8px;
                padding: 12px 14px; color: #86e1a8; }
            QLabel#status[error="true"] { color: #ff8a9a; border: 1px solid #713747; }
            QPushButton { min-height: 24px; padding: 12px 18px; border: none;
                border-radius: 8px; background-color: #7c4dff; color: white; font-weight: 600; }
            QPushButton:hover { background-color: #8f69ff; }
            QPushButton#secondaryButton { background-color: #34344b;
                border: 1px solid #4b4b68; }
            QPushButton#secondaryButton:hover { background-color: #44445f; }
        """)
        self.show_amounts(self.model.values)

    @staticmethod
    def make_spinbox(decimals: int, minimum: float, maximum: float) -> QDoubleSpinBox:
        field = QDoubleSpinBox()
        field.setLocale(QLocale(QLocale.Language.Russian, QLocale.Country.Russia))
        field.setDecimals(decimals)
        field.setRange(minimum, maximum)
        field.setSingleStep(1.0 if decimals == 2 else 0.1)
        field.setGroupSeparatorShown(True)
        field.setKeyboardTracking(True)
        return field

    @pyqtSlot(float)
    def publish_rates(self, _value: float) -> None:
        self.rates_edited.emit(self.usd_rate.value(), self.eur_rate.value())

    @pyqtSlot(dict)
    def show_amounts(self, values: dict) -> None:
        blockers = [QSignalBlocker(widget) for widget in (
            *self.fields.values(), self.usd_rate, self.eur_rate,
        )]
        try:
            for code, value in values.items():
                if self.fields[code].value() != float(value):
                    self.fields[code].setValue(float(value))
            self.usd_rate.setValue(float(self.model.usd_rate))
            self.eur_rate.setValue(float(self.model.eur_rate))
        finally:
            del blockers
        self._set_status_error(False)
        self.status.setText(
            f"Исходная валюта: {self.model.source}. При изменении курса её сумма сохраняется."
        )

    @pyqtSlot(str)
    def show_error(self, message: str) -> None:
        self._set_status_error(True)
        self.status.setText(message)

    def _set_status_error(self, enabled: bool) -> None:
        self.status.setProperty("error", enabled)
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))
    window = ConverterWindow()
    window.show()
    QTimer.singleShot(0, lambda: refresh_initial_geometry(window))
    return app.exec()


def refresh_initial_geometry(window: QWidget) -> None:
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
