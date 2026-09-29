import sys
from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from app.core.protocols.loader import load_protocol
from app.core.utils.schedule import compute_schedule
from app.ui.dialogs.start_dialog import StartDiffDialog
from app.ui.views.calendar_view import CalendarView
from app.ui.views.diff_list_panel import DiffListPanel
from app.data.database import get_db_path, init_db
from app.data.repositories import load_experiments, save_experiment


class MainWindow(QMainWindow):
    def __init__(self, protocol, protocol_key: str):
        super().__init__()
        self.setWindowTitle("Diff Tracker")
        self._protocol = protocol
        self._protocol_key = protocol_key
        self._diffs = load_experiments()

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(16)

        # ── header ───────────────────────────────────────────────────────
        header = QHBoxLayout()
        title = QLabel("Diff Tracker")
        tf = QFont()
        tf.setPointSize(22)
        tf.setBold(True)
        title.setFont(tf)
        title.setStyleSheet("color:#0F172A;")

        self._new_btn = QPushButton("+ New Diff")
        self._new_btn.setFixedHeight(40)
        self._new_btn.setCursor(Qt.PointingHandCursor)
        self._new_btn.setStyleSheet("""
            QPushButton {
                background:#3B82F6; color:#FFFFFF;
                border:none; border-radius:8px;
                padding:0 18px; font-size:11pt; font-weight:600;
            }
            QPushButton:hover { background:#2563EB; }
        """)
        self._new_btn.clicked.connect(self._new_diff)

        clear_btn = QPushButton("Clear DB")
        clear_btn.setFixedHeight(40)
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.setStyleSheet("""
            QPushButton {
                background:transparent; color:#94A3B8;
                border:1px solid #E2E8F0; border-radius:8px;
                padding:0 14px; font-size:11pt;
            }
            QPushButton:hover { color:#EF4444; border-color:#EF4444; }
        """)
        clear_btn.clicked.connect(self._clear_db)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(clear_btn)
        header.addSpacing(8)
        header.addWidget(self._new_btn)
        root.addLayout(header)

        # ── divider ──────────────────────────────────────────────────────
        div = QWidget()
        div.setFixedHeight(1)
        div.setStyleSheet("background:#E2E8F0;")
        root.addWidget(div)

        # ── split: calendar (left) | diff list (right) ───────────────────
        self._splitter = QSplitter(Qt.Horizontal)
        self._splitter.setHandleWidth(1)
        self._splitter.setStyleSheet(
            "QSplitter::handle { background:#E2E8F0; }"
        )

        self._calendar = CalendarView(self._diffs)
        self._diff_list = DiffListPanel(self._diffs)

        self._splitter.addWidget(self._calendar)
        self._splitter.addWidget(self._diff_list)
        self._splitter.setSizes([500, 650])

        root.addWidget(self._splitter, 1)

    def _rebuild_panels(self):
        # detach and schedule deletion of all current splitter children
        for i in reversed(range(self._splitter.count())):
            w = self._splitter.widget(i)
            w.setParent(None)
            w.deleteLater()
        self._calendar = CalendarView(self._diffs)
        self._diff_list = DiffListPanel(self._diffs)
        self._splitter.addWidget(self._calendar)
        self._splitter.addWidget(self._diff_list)
        self._splitter.setSizes([500, 650])

    def _clear_db(self):
        import sqlite3
        with sqlite3.connect(get_db_path()) as conn:
            conn.execute("DELETE FROM experiment_edges")
            conn.execute("DELETE FROM experiment_steps")
            conn.execute("DELETE FROM experiments")
        self._diffs.clear()
        self._rebuild_panels()

    def _new_diff(self):
        dialog = StartDiffDialog(self._protocol.name, self)
        if dialog.exec() != QDialog.Accepted:
            return
        name = dialog.name()
        start_date = dialog.start_date()
        schedule = compute_schedule(self._protocol, start_date)
        end_date = schedule[-1].date
        save_experiment(name, self._protocol, start_date, end_date)
        self._diffs = load_experiments()
        self._rebuild_panels()


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Inter", 13))

    palette = QPalette()
    palette.setColor(QPalette.Window,          QColor("#FAFAFA"))
    palette.setColor(QPalette.WindowText,      QColor("#0F172A"))
    palette.setColor(QPalette.Base,            QColor("#FFFFFF"))
    palette.setColor(QPalette.AlternateBase,   QColor("#F1F5F9"))
    palette.setColor(QPalette.Button,          QColor("#F1F5F9"))
    palette.setColor(QPalette.ButtonText,      QColor("#0F172A"))
    palette.setColor(QPalette.Highlight,       QColor("#3B82F6"))
    palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(palette)

    app.setStyleSheet("""
        QScrollBar:horizontal {
            height:6px; background:transparent; margin:0;
        }
        QScrollBar::handle:horizontal {
            background:#CBD5E1; border-radius:3px; min-width:40px;
        }
        QScrollBar::handle:horizontal:hover { background:#94A3B8; }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal
            { width:0; height:0; }
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal
            { background:transparent; }
        QScrollBar:vertical {
            width:6px; background:transparent; margin:0;
        }
        QScrollBar::handle:vertical {
            background:#CBD5E1; border-radius:3px; min-height:40px;
        }
        QScrollBar::handle:vertical:hover { background:#94A3B8; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical
            { width:0; height:0; }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical
            { background:transparent; }
    """)

    protocol_key = "allen"
    protocol = load_protocol(protocol_key)
    init_db()
    window = MainWindow(protocol, protocol_key)
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
