from datetime import date, timedelta

from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtGui import QColor, QFont, QTextCharFormat
from PySide6.QtWidgets import (
    QDateEdit,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.core.models.experiment import ScheduleEntry

_STYLE = """
QDialog { background: #FFFFFF; }
QLabel  { color: #0F172A; }
QDateEdit {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 6px 12px;
    color: #0F172A;
    font-size: 11pt;
}
QDateEdit:focus {
    border: 1px solid #3B82F6;
    background: #FFFFFF;
}
QDateEdit::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 28px;
    border: none;
    background: transparent;
}
QDateEdit::down-arrow {
    image: url(app/ui/resources/chevron_down.svg);
    width: 10px; height: 6px;
}
QPushButton#save {
    background: #3B82F6; color: #FFFFFF;
    border: none; border-radius: 8px;
    padding: 10px 0; font-size: 11pt; font-weight: 600;
}
QPushButton#save:hover { background: #2563EB; }
QPushButton#cancel {
    background: transparent; color: #64748B;
    border: 1px solid #E2E8F0; border-radius: 8px;
    padding: 10px 0; font-size: 11pt;
}
QPushButton#cancel:hover { background: #F8FAFC; }
"""


class _StepRow(QWidget):
    """Single editable step row."""

    date_changed = Signal(int, QDate)  # (row_index, new_qdate)

    def __init__(self, idx: int, entry: ScheduleEntry, today: date, parent=None):
        super().__init__(parent)
        self._idx = idx
        done = entry.date <= today

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(14)

        # dot
        dot = QFrame()
        dot.setFixedSize(10, 10)
        if done:
            dot.setStyleSheet("background:#3B82F6; border-radius:5px; border:none;")
        else:
            dot.setStyleSheet(
                "background:#FFFFFF; border-radius:5px; border:2px solid #3B82F6;"
            )
        dot.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(dot, 0, Qt.AlignVCenter)

        # step name
        name_lbl = QLabel(entry.step.name)
        nf = QFont()
        nf.setPointSize(11)
        nf.setBold(done)
        name_lbl.setFont(nf)
        name_lbl.setStyleSheet(
            f"color:{'#0F172A' if done else '#64748B'};"
        )
        name_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(name_lbl)

        # day badge (updated dynamically)
        self._day_lbl = QLabel(f"Day {entry.day_number}")
        self._day_lbl.setFixedWidth(54)
        self._day_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._day_lbl.setStyleSheet("color:#94A3B8; font-size:10pt;")
        layout.addWidget(self._day_lbl)

        # date edit
        self._date_edit = QDateEdit(
            QDate(entry.date.year, entry.date.month, entry.date.day)
        )
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDisplayFormat("MMM dd, yyyy")
        self._date_edit.setFixedWidth(148)
        self._style_calendar_popup()
        layout.addWidget(self._date_edit)

        self._date_edit.dateChanged.connect(
            lambda qd: self.date_changed.emit(self._idx, qd)
        )

    def _style_calendar_popup(self):
        cal = self._date_edit.calendarWidget()
        plain = QTextCharFormat()
        plain.setForeground(QColor("#0F172A"))
        cal.setWeekdayTextFormat(Qt.Saturday, plain)
        cal.setWeekdayTextFormat(Qt.Sunday, plain)
        cal.setStyleSheet("""
            QCalendarWidget QAbstractItemView {
                background:#FFFFFF; color:#0F172A;
                selection-background-color:#3B82F6;
                selection-color:#FFFFFF; font-size:10pt;
            }
            QCalendarWidget QAbstractItemView:disabled { color:#CBD5E1; }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background:#FFFFFF; padding:4px 8px;
            }
            QCalendarWidget QToolButton {
                color:#0F172A; background:transparent;
                font-size:11pt; font-weight:600;
                border:none; border-radius:6px; padding:4px 8px;
            }
            QCalendarWidget QToolButton:hover { background:#F1F5F9; }
            QCalendarWidget QToolButton::menu-indicator { image:none; width:0; }
            QCalendarWidget QSpinBox {
                color:#0F172A; background:#FFFFFF; border:none; font-size:11pt;
            }
        """)

    def set_date(self, d: date):
        self._date_edit.blockSignals(True)
        self._date_edit.setDate(QDate(d.year, d.month, d.day))
        self._date_edit.blockSignals(False)

    def set_day_number(self, n: int):
        self._day_lbl.setText(f"Day {n}")

    def current_date(self) -> date:
        qd = self._date_edit.date()
        return date(qd.year(), qd.month(), qd.day())


class EditDiffDialog(QDialog):
    def __init__(self, diff: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Edit — {diff['name']}")
        self.setMinimumWidth(560)
        self.setMinimumHeight(480)
        self.setStyleSheet(_STYLE)

        schedule: list[ScheduleEntry] = diff["schedule"]
        today = date.today()

        # mutable date list — source of truth while editing
        self._dates: list[date] = [e.date for e in schedule]
        self._step_ids: list[str] = [e.step.id for e in schedule]

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        # ── title ────────────────────────────────────────────────────────
        title = QLabel(diff["name"])
        tf = QFont()
        tf.setPointSize(15)
        tf.setBold(True)
        title.setFont(tf)
        root.addWidget(title)

        sub = QLabel("Editing a step date shifts all subsequent steps by the same delta.")
        sub.setStyleSheet("color:#94A3B8; font-size:10pt;")
        root.addWidget(sub)

        # ── divider ──────────────────────────────────────────────────────
        div = QWidget()
        div.setFixedHeight(1)
        div.setStyleSheet("background:#E2E8F0;")
        root.addWidget(div)

        # ── column headers ───────────────────────────────────────────────
        col_hdr = QHBoxLayout()
        col_hdr.setContentsMargins(24, 0, 0, 0)
        col_hdr.setSpacing(14)
        for text, stretch, width in [
            ("Step", True, None),
            ("Day", False, 54),
            ("Date", False, 148),
        ]:
            lbl = QLabel(text)
            lbl.setStyleSheet("color:#94A3B8; font-size:9pt; font-weight:600;")
            if width:
                lbl.setFixedWidth(width)
                lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if stretch:
                col_hdr.addWidget(lbl, 1)
            else:
                col_hdr.addWidget(lbl)
        root.addLayout(col_hdr)

        # ── scrollable step rows ─────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        container.setStyleSheet("background:#FFFFFF;")
        self._vbox = QVBoxLayout(container)
        self._vbox.setContentsMargins(0, 0, 0, 0)
        self._vbox.setSpacing(0)

        self._rows: list[_StepRow] = []
        for i, entry in enumerate(schedule):
            row = _StepRow(i, entry, today)
            row.date_changed.connect(self._on_date_changed)
            self._rows.append(row)
            self._vbox.addWidget(row)

            # thin separator between rows
            if i < len(schedule) - 1:
                sep = QFrame()
                sep.setFrameShape(QFrame.HLine)
                sep.setStyleSheet("background:#F1F5F9; border:none;")
                sep.setFixedHeight(1)
                self._vbox.addWidget(sep)

        self._vbox.addStretch()
        scroll.setWidget(container)
        root.addWidget(scroll, 1)

        # ── buttons ──────────────────────────────────────────────────────
        div2 = QWidget()
        div2.setFixedHeight(1)
        div2.setStyleSheet("background:#E2E8F0;")
        root.addWidget(div2)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        cancel = QPushButton("Cancel")
        cancel.setObjectName("cancel")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Save Changes")
        save.setObjectName("save")
        save.clicked.connect(self.accept)
        btn_row.addWidget(cancel)
        btn_row.addWidget(save)
        root.addLayout(btn_row)

    def _on_date_changed(self, idx: int, new_qdate: QDate):
        new_date = date(new_qdate.year(), new_qdate.month(), new_qdate.day())
        delta = new_date - self._dates[idx]
        if delta.days == 0:
            return

        # shift this step and all subsequent ones
        for i in range(idx, len(self._dates)):
            self._dates[i] += delta

        # update subsequent row widgets (current row already shows correct value)
        for i in range(idx + 1, len(self._rows)):
            self._rows[i].set_date(self._dates[i])

        # recompute and update all day number labels
        start = self._dates[0]
        for i, row in enumerate(self._rows):
            row.set_day_number((self._dates[i] - start).days)

    def updated_dates(self) -> list[tuple[str, date]]:
        """Returns [(step_id, new_date), ...] for the backend to persist."""
        return list(zip(self._step_ids, self._dates))
