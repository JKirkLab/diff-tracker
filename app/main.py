import sys
from datetime import date, timedelta

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


def _make_diff(protocol, name: str, days_ago: int) -> dict:
    start = date.today() - timedelta(days=days_ago)
    return {
        "name": name,
        "protocol": protocol,
        "schedule": compute_schedule(protocol, start),
        "start_date": start,
    }


class MainWindow(QMainWindow):
    def __init__(self, protocol):
        super().__init__()
        self.setWindowTitle("Diff Tracker")
        self._protocol = protocol

        self._diffs = [
            _make_diff(protocol, "Batch 3 — Well A1", 12),
            _make_diff(protocol, "Batch 4 — Well B2", 6),
            _make_diff(protocol, "Batch 5 — Well C3", 0),
        ]

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(16)

        # ── header ───────────────────────────────────────────────────────
        header = QHBoxLayout()
        title = QLabel("Diff Tracker")
        tf = QFont()
        tf.setPointSize(20)
        tf.setBold(True)
        title.setFont(tf)
        title.setStyleSheet("color:#0F172A;")

        self._new_btn = QPushButton("+ New Diff")
        self._new_btn.setFixedHeight(36)
        self._new_btn.setCursor(Qt.PointingHandCursor)
        self._new_btn.setStyleSheet("""
            QPushButton {
                background:#3B82F6; color:#FFFFFF;
                border:none; border-radius:8px;
                padding:0 18px; font-size:10pt; font-weight:600;
            }
            QPushButton:hover { background:#2563EB; }
        """)
        self._new_btn.clicked.connect(self._new_diff)

        header.addWidget(title)
        header.addStretch()
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
        self._splitter.setSizes([600, 400])

        root.addWidget(self._splitter, 1)

    def _new_diff(self):
        dialog = StartDiffDialog(self._protocol.name, self)
        if dialog.exec() != QDialog.Accepted:
            return
        start_date = dialog.start_date()
        diff = {
            "name": dialog.name(),
            "protocol": self._protocol,
            "schedule": compute_schedule(self._protocol, start_date),
            "start_date": start_date,
        }
        self._diffs.append(diff)
        # rebuild both panels
        self._splitter.replaceWidget(0, CalendarView(self._diffs))
        self._splitter.replaceWidget(1, DiffListPanel(self._diffs))
        self._splitter.setSizes([600, 400])


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Inter", 11))

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

    protocol = load_protocol("allen")
    window = MainWindow(protocol)
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
