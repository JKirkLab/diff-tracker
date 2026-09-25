from datetime import date

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
)


class StartDiffDialog(QDialog):
    """Asks the user for the Day 0 start date of a differentiation."""

    def __init__(self, protocol_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Start — {protocol_name}")
        self.setMinimumWidth(300)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        layout.addWidget(QLabel("<b>Protocol</b>"))
        layout.addWidget(QLabel(protocol_name))

        layout.addWidget(QLabel("<b>Start date (Day 0)</b>"))
        self._date_edit = QDateEdit(QDate.currentDate())
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDisplayFormat("yyyy-MM-dd")
        layout.addWidget(self._date_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def start_date(self) -> date:
        qd = self._date_edit.date()
        return date(qd.year(), qd.month(), qd.day())