import sys
from pathlib import Path

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel
from PyQt6.QtWidgets import (
    QAbstractItemView, QApplication, QComboBox, QFileDialog, QFrame,
    QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QMainWindow,
    QMessageBox, QPushButton, QTableView, QTabWidget, QVBoxLayout, QWidget,
)


class SqlBrowserWindow(QMainWindow):
    """Окно задания: подключение к БД и пять результатов запросов."""

    CONNECTION_NAME = "gui_lab3_connection"

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ЛР 3")
        self.resize(1100, 720)
        self.setMinimumSize(820, 560)
        self.database: QSqlDatabase | None = None
        self.models: list[QSqlQueryModel | None] = [None] * 5
        self._build_menu()

        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(28, 24, 28, 26)
        root.setSpacing(16)
        heading = QLabel("Обозреватель SQLite")
        heading.setObjectName("title")
        subtitle = QLabel("Подключите базу данных и исследуйте её структуру")
        subtitle.setObjectName("subtitle")
        root.addWidget(heading)
        root.addWidget(subtitle)

        control_card = QFrame()
        control_card.setObjectName("card")
        controls = QHBoxLayout(control_card)
        controls.setContentsMargins(18, 18, 18, 18)
        controls.setSpacing(12)
        self.bt1 = QPushButton("Имена объектов")
        self.bt1.setObjectName("bt1")
        self.columns = QComboBox()
        self.columns.setObjectName("columns")
        self.columns.setMinimumWidth(220)
        self.columns.setPlaceholderText("Выберите колонку")
        self.bt2 = QPushButton("Подробности")
        self.bt2.setObjectName("bt2")
        self.bt3 = QPushButton("Статистика")
        self.bt3.setObjectName("bt3")
        controls.addWidget(self.bt1)
        controls.addWidget(self.columns, 1)
        controls.addWidget(self.bt2)
        controls.addWidget(self.bt3)
        root.addWidget(control_card)

        shadow = QGraphicsDropShadowEffect(heading)
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 3)
        shadow.setColor(Qt.GlobalColor.black)
        heading.setGraphicsEffect(shadow)

        self.tabs = QTabWidget()
        self.views: list[QTableView] = []
        titles = ("Структура", "Имена", "Колонка", "Подробности", "Статистика")
        for title in titles:
            view = QTableView()
            view.setAlternatingRowColors(True)
            view.setSortingEnabled(True)
            view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            view.horizontalHeader().setStretchLastSection(True)
            self.views.append(view)
            self.tabs.addTab(view, title)
        root.addWidget(self.tabs, 1)

        self.status = QLabel("База данных не подключена")
        self.status.setObjectName("status")
        self.status.setWordWrap(True)
        root.addWidget(self.status)
        self.bt1.clicked.connect(self.select_name_query)
        self.columns.currentTextChanged.connect(self.column_query)
        self.bt2.clicked.connect(self.query_two)
        self.bt3.clicked.connect(self.query_three)
        self.set_controls_enabled(False)
        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #1e1e2e; color: #ffffff;
                font-family: "Segoe UI"; font-size: 10pt; }
            QLabel { background: transparent; }
            QLabel#title { font-size: 19pt; font-weight: 700; }
            QLabel#subtitle { color: #aaa7c2; margin-bottom: 4px; }
            QFrame#card { background-color: #252538; border: 1px solid #393950;
                border-radius: 12px; }
            QPushButton { min-height: 22px; padding: 10px 16px; border: none;
                border-radius: 8px; background-color: #7c4dff; color: white;
                font-weight: 600; }
            QPushButton:hover { background-color: #8f69ff; }
            QPushButton:pressed { background-color: #6838e6; }
            QPushButton:disabled { background-color: #323246; color: #6f6d82; }
            QComboBox { min-height: 22px; padding: 9px 12px; background-color: #191927;
                border: 1px solid #45455f; border-radius: 8px; color: #ffffff; }
            QComboBox:focus { border: 2px solid #7c4dff; padding: 8px 11px; }
            QComboBox QAbstractItemView { background-color: #252538; color: white;
                border: 1px solid #45455f; selection-background-color: #7c4dff; }
            QTabWidget::pane { background-color: #252538; border: 1px solid #393950;
                border-radius: 8px; top: -1px; }
            QTabBar::tab { background-color: #252538; color: #aaa7c2;
                padding: 10px 18px; margin-right: 3px; border-top-left-radius: 8px;
                border-top-right-radius: 8px; }
            QTabBar::tab:selected { background-color: #7c4dff; color: white; }
            QTableView { background-color: #202031; alternate-background-color: #29293d;
                color: #eeeeff; gridline-color: #393950; border: none; selection-background-color: #6541cc; }
            QHeaderView::section { background-color: #303047; color: #c9c6da;
                border: none; border-right: 1px solid #45455f; padding: 9px; font-weight: 600; }
            QLabel#status { color: #aaa7c2; background-color: #252538;
                border-radius: 8px; padding: 10px 14px; }
            QMenuBar { background-color: #181824; color: white; padding: 3px; }
            QMenuBar::item:selected, QMenu::item:selected { background-color: #7c4dff; }
            QMenu { background-color: #252538; color: white; border: 1px solid #45455f; }
            QMenu::item { padding: 8px 28px; }
        """)

    def _build_menu(self) -> None:
        menu = self.menuBar().addMenu("База данных")
        connect = QAction("Открыть соединение…", self)
        connect.setShortcut("Ctrl+O")
        connect.triggered.connect(self.choose_database)
        close = QAction("Закрыть соединение", self)
        close.setShortcut("Ctrl+W")
        close.triggered.connect(self.close_database)
        menu.addAction(connect)
        menu.addAction(close)

    def set_controls_enabled(self, enabled: bool) -> None:
        for widget in (self.bt1, self.columns, self.bt2, self.bt3):
            widget.setEnabled(enabled)

    def choose_database(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Выберите базу SQLite", str(Path.home()),
            "SQLite database (*.db *.sqlite *.sqlite3);;All files (*)",
        )
        if path:
            self.open_database(path)

    def open_database(self, path: str) -> bool:
        self.close_database(clear_status=False)
        self.database = QSqlDatabase.addDatabase("QSQLITE", self.CONNECTION_NAME)
        self.database.setDatabaseName(path)
        if not self.database.open():
            message = self.database.lastError().text()
            self.database = None
            QSqlDatabase.removeDatabase(self.CONNECTION_NAME)
            QMessageBox.critical(self, "Ошибка подключения", message)
            self.status.setText("Не удалось открыть базу данных")
            return False
        self.set_controls_enabled(True)
        self.status.setText(f"Подключено: {path}")
        self.run_query("SELECT * FROM sqlite_master", 0)
        self.load_columns()
        return True

    def close_database(self, clear_status: bool = True) -> None:
        self.set_controls_enabled(False)
        self.columns.clear()
        for index, view in enumerate(self.views):
            view.setModel(None)
            model = self.models[index]
            if model is not None:
                model.setQuery(QSqlQuery())
                model.deleteLater()
        self.models = [None] * 5
        if self.database is not None:
            connection = self.database.connectionName()
            self.database.close()
            self.database = None
            QSqlDatabase.removeDatabase(connection)
        if clear_status:
            self.status.setText("База данных закрыта")

    def run_query(self, sql: str, tab_index: int) -> bool:
        if self.database is None or not self.database.isOpen():
            return False
        model = QSqlQueryModel(self)
        model.setQuery(sql, self.database)
        if model.lastError().isValid():
            QMessageBox.warning(self, "Ошибка SQL", model.lastError().text())
            model.deleteLater()
            return False
        old_model = self.models[tab_index]
        if old_model is not None:
            old_model.setQuery(QSqlQuery())
            old_model.deleteLater()
        self.models[tab_index] = model
        self.views[tab_index].setModel(model)
        self.views[tab_index].resizeColumnsToContents()
        self.tabs.setCurrentIndex(tab_index)
        self.status.setText(f"Выполнен запрос: {sql}")
        return True

    def load_columns(self) -> None:
        self.columns.blockSignals(True)
        self.columns.clear()
        query = QSqlQuery(self.database)
        if query.exec("PRAGMA table_info(sqlite_master)"):
            while query.next():
                self.columns.addItem(str(query.value(1)))
        self.columns.setCurrentIndex(-1)
        self.columns.blockSignals(False)

    def select_name_query(self) -> None:
        self.run_query("SELECT name FROM sqlite_master", 1)

    def column_query(self, column: str) -> None:
        if not column or self.database is None:
            return
        identifier = '"' + column.replace('"', '""') + '"'
        self.run_query(f"SELECT {identifier} FROM sqlite_master", 2)

    def query_two(self) -> None:
        self.run_query(
            "SELECT type, name, tbl_name, rootpage, sql "
            "FROM sqlite_master ORDER BY type, name", 3,
        )

    def query_three(self) -> None:
        self.run_query(
            "SELECT type, COUNT(*) AS object_count "
            "FROM sqlite_master GROUP BY type ORDER BY type", 4,
        )

    def closeEvent(self, event) -> None:
        self.close_database(clear_status=False)
        event.accept()


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))
    window = SqlBrowserWindow()
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
