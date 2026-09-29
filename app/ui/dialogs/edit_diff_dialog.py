from datetime import date

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
    clicked = Signal(int)

    def __init__(self, idx: int, entry: ScheduleEntry, today: date, parent=None):
        super().__init__(parent)
        self._idx = idx
        self._entry = entry
        self._selected = False
        self._current_date = entry.date

        self.setFixedHeight(52)
        self.setCursor(Qt.PointingHandCursor)
        self._apply_style()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(14)

        done = entry.date <= today

        dot = QFrame()
        dot.setFixedSize(10, 10)
        dot.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        dot.setAttribute(Qt.WA_TransparentForMouseEvents)
        if done:
            dot.setStyleSheet("background:#3B82F6; border-radius:5px; border:none;")
        else:
            dot.setStyleSheet("background:#FFFFFF; border-radius:5px; border:2px solid #3B82F6;")
        layout.addWidget(dot, 0, Qt.AlignVCenter)

        name_lbl = QLabel(entry.step.name)
        nf = QFont()
        nf.setPointSize(11)
        nf.setBold(done)
        name_lbl.setFont(nf)
        name_lbl.setStyleSheet(f"color:{'#0F172A' if done else '#64748B'};")
        name_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        name_lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
        layout.addWidget(name_lbl)

        self._day_lbl = QLabel(f"Day {entry.day_number}")
        self._day_lbl.setFixedWidth(54)
        self._day_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._day_lbl.setStyleSheet("color:#94A3B8; font-size:10pt;")
        self._day_lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
        layout.addWidget(self._day_lbl)

        # static date label (shown when not selected)
        self._date_lbl = QLabel(entry.date.strftime("%b %d, %Y"))
        self._date_lbl.setFixedWidth(148)
        self._date_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._date_lbl.setStyleSheet("color:#64748B; font-size:10pt;")
        self._date_lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
        layout.addWidget(self._date_lbl)

        # date picker (shown only when selected)
        self._date_edit = QDateEdit(QDate(entry.date.year, entry.date.month, entry.date.day))
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDisplayFormat("MMM dd, yyyy")
        self._date_edit.setFixedWidth(148)
        self._style_calendar_popup()
        self._date_edit.setVisible(False)
        layout.addWidget(self._date_edit)

    def mousePressEvent(self, event):
        self.clicked.emit(self._idx)
        super().mousePressEvent(event)

    def _apply_style(self):
        if self._selected:
            self.setStyleSheet("QWidget { background: #EFF6FF; border-radius: 8px; }")
        else:
            self.setStyleSheet("QWidget { background: transparent; border-radius: 8px; }")

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

    def set_selected(self, selected: bool):
        self._selected = selected
        self._date_lbl.setVisible(not selected)
        self._date_edit.setVisible(selected)
        self._apply_style()

    def set_date(self, d: date):
        self._current_date = d
        self._date_lbl.setText(d.strftime("%b %d, %Y"))
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

        self._dates: list[date] = [e.date for e in schedule]
        self._step_ids: list[str] = [e.step.id for e in schedule]
        self._selected_idx: int | None = None
        self._delta: int = 0

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        title = QLabel(diff["name"])
        tf = QFont()
        tf.setPointSize(15)
        tf.setBold(True)
        title.setFont(tf)
        root.addWidget(title)

        sub = QLabel("Select a step to change its date. All subsequent steps shift by the same delta.")
        sub.setStyleSheet("color:#94A3B8; font-size:10pt;")
        root.addWidget(sub)

        div = QWidget()
        div.setFixedHeight(1)
        div.setStyleSheet("background:#E2E8F0;")
        root.addWidget(div)

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
            row.clicked.connect(self._select_row)
            self._rows.append(row)
            self._vbox.addWidget(row)

            if i < len(schedule) - 1:
                sep = QFrame()
                sep.setFrameShape(QFrame.HLine)
                sep.setStyleSheet("background:#F1F5F9; border:none;")
                sep.setFixedHeight(1)
                self._vbox.addWidget(sep)

        self._vbox.addStretch()
        scroll.setWidget(container)
        root.addWidget(scroll, 1)

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
        save.clicked.connect(self._save)
        btn_row.addWidget(cancel)
        btn_row.addWidget(save)
        root.addLayout(btn_row)

    def _select_row(self, idx: int):
        if self._selected_idx == idx:
            return
        if self._selected_idx is not None:
            self._rows[self._selected_idx].set_selected(False)
        self._selected_idx = idx
        self._rows[idx].set_selected(True)

    def _save(self):
        self._delta = 0
        if self._selected_idx is not None:
            idx = self._selected_idx
            new_date = self._rows[idx].current_date()
            self._delta = (new_date - self._dates[idx]).days

        self.accept()

    def edit_result(self) -> tuple[str, int] | None:
        """Returns (step_id, delta_days) for the edited step, or None if nothing was changed."""
        if self._selected_idx is None or self._delta == 0:
            return None
        return (self._step_ids[self._selected_idx], self._delta)