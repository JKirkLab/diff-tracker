from datetime import date

from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QColor, QTextCharFormat
from PySide6.QtWidgets import (
    QDateEdit,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

_STYLE = """
QDialog {
    background: #FFFFFF;
}
QLabel {
    color: #0F172A;
    font-size: 11pt;
}
QLabel#sub {
    color: #64748B;
    font-size: 10pt;
}
QLineEdit, QDateEdit {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 10px 14px;
    color: #0F172A;
    font-size: 11pt;
}
QLineEdit:focus, QDateEdit:focus {
    border: 1px solid #3B82F6;
    background: #FFFFFF;
}
QDateEdit::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 32px;
    border: none;
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
    background: transparent;
}
QDateEdit::down-arrow {
    image: url(app/ui/resources/chevron_down.svg);
    width: 10px;
    height: 6px;
}
QPushButton#ok {
    background: #3B82F6;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 11pt;
    font-weight: 600;
}
QPushButton#ok:hover   { background: #2563EB; }
QPushButton#ok:disabled { background: #CBD5E1; color: #94A3B8; }
QPushButton#cancel {
    background: transparent;
    color: #64748B;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 10px 0;
    font-size: 11pt;
}
QPushButton#cancel:hover { background: #F8FAFC; }
QPushButton#ok { padding: 10px 0; }
"""


class StartDiffDialog(QDialog):
    def __init__(self, protocol_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New differentiation")
        self.setMinimumWidth(360)
        self.setStyleSheet(_STYLE)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(28, 28, 28, 28)

        # Protocol label
        proto_lbl = QLabel(protocol_name)
        proto_lbl.setObjectName("sub")
        layout.addWidget(proto_lbl)

        # Experiment name
        layout.addWidget(QLabel("Experiment name"))
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("e.g. Batch 3 — well A1")
        layout.addWidget(self._name_edit)

        # Start date
        layout.addWidget(QLabel("Start date (Day 0)"))
        self._date_edit = QDateEdit(QDate.currentDate())
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDisplayFormat("yyyy-MM-dd")
        layout.addWidget(self._date_edit)
        self._style_calendar_popup()

        layout.addSpacing(8)

        # Buttons (manual so we can name them for stylesheet)
        self._ok = QPushButton("Start")
        self._ok.setObjectName("ok")
        self._ok.setEnabled(False)
        self._ok.clicked.connect(self._on_accept)

        cancel = QPushButton("Cancel")
        cancel.setObjectName("cancel")
        cancel.clicked.connect(self.reject)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addWidget(cancel)
        btn_row.addWidget(self._ok)
        layout.addLayout(btn_row)

        self._name_edit.textChanged.connect(
            lambda t: self._ok.setEnabled(bool(t.strip()))
        )

    def _style_calendar_popup(self):
        cal = self._date_edit.calendarWidget()

        # Kill the default red weekends
        normal_fmt = QTextCharFormat()
        normal_fmt.setForeground(QColor("#0F172A"))
        cal.setWeekdayTextFormat(Qt.Saturday, normal_fmt)
        cal.setWeekdayTextFormat(Qt.Sunday, normal_fmt)

        cal.setStyleSheet("""
            QCalendarWidget {
                background: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
            }
            QCalendarWidget QAbstractItemView {
                background: #FFFFFF;
                color: #0F172A;
                selection-background-color: #3B82F6;
                selection-color: #FFFFFF;
                outline: none;
                font-size: 10pt;
            }
            QCalendarWidget QAbstractItemView:disabled { color: #CBD5E1; }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background: #FFFFFF;
                padding: 4px 8px;
            }
            QCalendarWidget QToolButton {
                color: #0F172A;
                background: transparent;
                font-size: 11pt;
                font-weight: 600;
                border: none;
                border-radius: 6px;
                padding: 4px 8px;
            }
            QCalendarWidget QToolButton:hover { background: #F1F5F9; }
            QCalendarWidget QToolButton::menu-indicator { image: none; width: 0; }
            QCalendarWidget QMenu {
                background: #FFFFFF;
                color: #0F172A;
                border: 1px solid #E2E8F0;
            }
            QCalendarWidget QSpinBox {
                color: #0F172A;
                background: #FFFFFF;
                border: none;
                font-size: 11pt;
            }
        """)

    def _on_accept(self):
        if self._name_edit.text().strip():
            self.accept()

    def name(self) -> str:
        return self._name_edit.text().strip()

    def start_date(self) -> date:
        qd = self._date_edit.date()
        return date(qd.year(), qd.month(), qd.day())