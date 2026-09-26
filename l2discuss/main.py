import os
import sys
from pathlib import Path

from PyQt5 import QtCore


plugins = Path(QtCore.__file__).resolve().parent / "Qt5" / "plugins"
if (plugins / "platforms").is_dir():
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(plugins)
    QtCore.QCoreApplication.addLibraryPath(str(plugins))

from PyQt5.QtCore import QLocale, QSignalBlocker, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (
    QApplication, QDoubleSpinBox, QFormLayout, QGroupBox, QLabel,
    QPushButton, QVBoxLayout, QWidget,
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

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ЛР 2 — Конвертер валют: сигналы и слоты")
        self.setMinimumWidth(550)
        self.model = CurrencyModel(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        intro = QLabel("Измените сумму в любой валюте — остальные поля пересчитаются.")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        amounts = QGroupBox("Суммы")
        form = QFormLayout(amounts)
        self.fields = {}
        for code, title in (("RUB", "Рубли (RUB)"), ("USD", "Доллары (USD)"), ("EUR", "Евро (EUR)")):
            field = self.make_spinbox(2, 0, float(MAX_AMOUNT))
            field.setObjectName(code)
            field.setAccessibleName(title)
            field.valueChanged.connect(
                lambda value, currency=code: self.amount_edited.emit(currency, value)
            )
            self.fields[code] = field
            form.addRow(title, field)
        layout.addWidget(amounts)
        rates = QGroupBox("Учебные курсы — задаются вручную")
        rate_form = QFormLayout(rates)
        self.usd_rate = self.make_spinbox(4, float(MIN_RATE), float(MAX_RATE))
        self.eur_rate = self.make_spinbox(4, float(MIN_RATE), float(MAX_RATE))
        rate_form.addRow("Рублей за 1 USD", self.usd_rate)
        rate_form.addRow("Рублей за 1 EUR", self.eur_rate)
        self.usd_rate.valueChanged.connect(self.publish_rates)
        self.eur_rate.valueChanged.connect(self.publish_rates)
        layout.addWidget(rates)
        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        self.amount_edited.connect(self.model.set_amount)
        self.rates_edited.connect(self.model.set_rates)
        self.model.amounts_changed.connect(self.show_amounts)
        self.model.error_occurred.connect(self.show_error)
        self.show_amounts(self.model.values)

    @staticmethod
    def make_spinbox(decimals, minimum, maximum):
        field = QDoubleSpinBox()
        field.setLocale(QLocale(QLocale.Russian, QLocale.Russia))
        field.setDecimals(decimals)
        field.setRange(minimum, maximum)
        field.setSingleStep(1.0 if decimals == 2 else 0.1)
        field.setGroupSeparatorShown(True)
        field.setKeyboardTracking(True)
        field.setMinimumWidth(260)
        return field

    @pyqtSlot(float)
    def publish_rates(self, _value):
        self.rates_edited.emit(self.usd_rate.value(), self.eur_rate.value())

    @pyqtSlot(dict)
    def show_amounts(self, values):
        widgets = [*self.fields.values(), self.usd_rate, self.eur_rate]
        blockers = [QSignalBlocker(widget) for widget in widgets]
        try:
            for code, value in values.items():
                # Не переписываем текущий ввод тем же числом: сохраняем курсор.
                if self.fields[code].value() != float(value):
                    self.fields[code].setValue(float(value))
            self.usd_rate.setValue(float(self.model.usd_rate))
            self.eur_rate.setValue(float(self.model.eur_rate))
        finally:
            for blocker in blockers:
                blocker.unblock()
        self.status.setStyleSheet("color: #285839;")
        self.status.setText(
            f"Исходная валюта: {self.model.source}. При изменении курса её сумма сохраняется."
        )

    @pyqtSlot(str)
    def show_error(self, message):
        self.status.setStyleSheet("color: #a21b1b;")
        self.status.setText(message)


def main():
    app = QApplication(sys.argv)
    window = ConverterWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())