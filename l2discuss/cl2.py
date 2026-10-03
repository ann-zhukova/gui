from decimal import Decimal
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

if __package__:
    from .currency import convert, number
else:
    from currency import convert, number


class CurrencyModel(QObject):
    amounts_changed = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.source = "RUB"
        self.amount = Decimal("9000")
        self.usd_rate = Decimal("90")
        self.eur_rate = Decimal("100")
        self.values = convert(self.amount, self.source, self.usd_rate, self.eur_rate)

    @pyqtSlot(str, float)
    def set_amount(self, currency, amount):
        self._update(currency, amount, self.usd_rate, self.eur_rate)

    @pyqtSlot(float, float)
    def set_rates(self, usd_rate, eur_rate):
        self._update(self.source, self.amount, usd_rate, eur_rate)

    def _update(self, source, amount, usd_rate, eur_rate):
        try:
            values = convert(amount, source, usd_rate, eur_rate)
        except ValueError as exc:
            self.amounts_changed.emit(dict(self.values))
            self.error_occurred.emit(str(exc))
            return
        self.source = source
        self.amount = number(amount)
        self.usd_rate, self.eur_rate = number(usd_rate), number(eur_rate)
        self.values = values
        self.amounts_changed.emit(dict(values))
