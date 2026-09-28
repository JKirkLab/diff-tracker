from datetime import date

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.core.models.experiment import ScheduleEntry
from app.core.models.protocol import Protocol
from app.ui.views.calendar_view import CalendarView
from app.ui.views.timeline_view import TimelineView

_ACTIVE = (
    "QPushButton { background:#1E293B; color:#FFFFFF;"
    " border:none; border-radius:4px; padding:4px 16px; }"
)
_INACTIVE = (
    "QPushButton { background:transparent; color:#64748B;"
    " border:none; border-radius:4px; padding:4px 16px; }"
    "QPushButton:hover { background:#F1F5F9; color:#1E293B; }"
)


class _ViewToggle(QWidget):
    def __init__(self, stack: QStackedWidget, labels: list[str], parent=None):
        super().__init__(parent)
        self._stack = stack
        self._btns: list[QPushButton] = []
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        self.setStyleSheet("QWidget { background:#F1F5F9; border-radius:6px; }")
        self.setFixedHeight(32)
        for i, lbl in enumerate(labels):
            btn = QPushButton(lbl)
            btn.setFont(QFont("", 9))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            btn.clicked.connect(lambda _, ix=i: self._select(ix))
            layout.addWidget(btn)
            self._btns.append(btn)
        self._select(0)

    def _select(self, idx: int):
        self._stack.setCurrentIndex(idx)
        for i, b in enumerate(self._btns):
            b.setStyleSheet(_ACTIVE if i == idx else _INACTIVE)


class DiffDetailView(QWidget):
    back = Signal()

    def __init__(
        self,
        protocol: Protocol,
        schedule: list[ScheduleEntry],
        start_date: date,
        exp_name: str,
        parent=None,
    ):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(12)

        # ── top bar ──────────────────────────────────────────────────────
        top = QHBoxLayout()

        back_btn = QPushButton("← Back")
        back_btn.setStyleSheet(
            "QPushButton { background:transparent; color:#64748B;"
            " border:none; font-size:11pt; padding:0; }"
            "QPushButton:hover { color:#0F172A; }"
        )
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.clicked.connect(self.back)

        name_lbl = QLabel(exp_name)
        f = QFont()
        f.setPointSize(16)
        f.setBold(True)
        name_lbl.setFont(f)

        meta_lbl = QLabel(
            f"{protocol.name}  ·  Started {start_date.strftime('%B %d, %Y')}  ·  "
            f"Day 0 → Day {schedule[-1].day_number}"
        )
        meta_lbl.setStyleSheet("color:#64748B; font-size:10pt;")

        top.addWidget(back_btn)
        top.addSpacing(16)
        top.addWidget(name_lbl)
        top.addSpacing(12)
        top.addWidget(meta_lbl)
        top.addStretch()
        root.addLayout(top)

        # ── divider ──────────────────────────────────────────────────────
        div = QWidget()
        div.setFixedHeight(1)
        div.setStyleSheet("background:#E2E8F0;")
        root.addWidget(div)

        # ── stacked views ────────────────────────────────────────────────
        stack = QStackedWidget()
        stack.addWidget(CalendarView(schedule, start_date))
        stack.addWidget(TimelineView(schedule, start_date))

        toggle = _ViewToggle(stack, ["Calendar", "Timeline"])
        toggle_row = QHBoxLayout()
        toggle_row.addStretch()
        toggle_row.addWidget(toggle)
        root.addLayout(toggle_row)
        root.addWidget(stack, 1)
