import calendar
from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# Step colours cycle through this palette
STEP_COLORS = [
    ("#2563EB", "#EFF6FF"),  # blue
    ("#059669", "#ECFDF5"),  # green
    ("#D97706", "#FFFBEB"),  # amber
    ("#7C3AED", "#F5F3FF"),  # violet
    ("#DC2626", "#FEF2F2"),  # red
]


class DayCell(QFrame):
    def __init__(self, day_num: int, steps: list[dict], is_today: bool = False):
        super().__init__()
        self.setMinimumSize(110, 80)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(3)

        # Day number
        num_label = QLabel(str(day_num))
        num_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        f = QFont()
        f.setPointSize(9)
        if is_today:
            f.setBold(True)
        num_label.setFont(f)
        num_label.setStyleSheet("color: #1e293b;" if not is_today else "color: #2563EB;")
        layout.addWidget(num_label)

        for entry in steps:
            idx = entry["day_number"] % len(STEP_COLORS)
            fg, bg = STEP_COLORS[idx]
            chip = QLabel(f"D{entry['day_number']} · {entry['step']['name']}")
            chip.setWordWrap(True)
            chip.setToolTip(entry["step"]["description"])
            chip.setFont(QFont("", 7))
            chip.setStyleSheet(
                f"background: {bg}; color: {fg}; border: 1px solid {fg};"
                " border-radius: 3px; padding: 2px 4px;"
            )
            layout.addWidget(chip)

        layout.addStretch()

        border = "#93C5FD" if is_today else "#E2E8F0"
        bg_fill = "#EFF6FF" if is_today else "#FFFFFF"
        self.setStyleSheet(
            f"QFrame {{ background: {bg_fill}; border: 1px solid {border};"
            " border-radius: 6px; }}"
        )


class CalendarView(QWidget):
    def __init__(self, schedule: list[dict], start_date: date, parent=None):
        super().__init__(parent)
        self.schedule = schedule
        self.start_date = start_date
        self.current_year = start_date.year
        self.current_month = start_date.month

        # date → list of step entries
        self._date_index: dict[date, list[dict]] = {}
        for entry in schedule:
            self._date_index.setdefault(entry["date"], []).append(entry)

        self._build_shell()
        self._render()

    # ------------------------------------------------------------------
    def _build_shell(self):
        root = QVBoxLayout(self)
        root.setSpacing(8)
        root.setContentsMargins(0, 0, 0, 0)

        # Nav header
        nav = QHBoxLayout()
        self._prev_btn = QPushButton("‹")
        self._prev_btn.setFixedSize(28, 28)
        self._prev_btn.setCursor(Qt.PointingHandCursor)
        self._prev_btn.clicked.connect(self._prev_month)

        self._month_lbl = QLabel()
        self._month_lbl.setAlignment(Qt.AlignCenter)
        f = QFont()
        f.setPointSize(13)
        f.setBold(True)
        self._month_lbl.setFont(f)

        self._next_btn = QPushButton("›")
        self._next_btn.setFixedSize(28, 28)
        self._next_btn.setCursor(Qt.PointingHandCursor)
        self._next_btn.clicked.connect(self._next_month)

        nav.addWidget(self._prev_btn)
        nav.addWidget(self._month_lbl, 1)
        nav.addWidget(self._next_btn)
        root.addLayout(nav)

        # Weekday header row
        dow_row = QHBoxLayout()
        dow_row.setSpacing(4)
        for name in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
            lbl = QLabel(name)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFixedHeight(20)
            lbl.setFont(QFont("", 8))
            lbl.setStyleSheet("color: #64748B; font-weight: 600;")
            dow_row.addWidget(lbl, 1)
        root.addLayout(dow_row)

        # Grid container (replaced each render)
        self._grid_container = QWidget()
        self._grid_layout = QGridLayout(self._grid_container)
        self._grid_layout.setSpacing(4)
        root.addWidget(self._grid_container)

    def _render(self):
        # Clear
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._month_lbl.setText(
            date(self.current_year, self.current_month, 1).strftime("%B %Y")
        )

        today = date.today()
        weeks = calendar.monthcalendar(self.current_year, self.current_month)

        for row, week in enumerate(weeks):
            for col, day in enumerate(week):
                if day == 0:
                    placeholder = QFrame()
                    placeholder.setMinimumSize(110, 80)
                    self._grid_layout.addWidget(placeholder, row, col)
                else:
                    d = date(self.current_year, self.current_month, day)
                    cell = DayCell(
                        day_num=day,
                        steps=self._date_index.get(d, []),
                        is_today=(d == today),
                    )
                    self._grid_layout.addWidget(cell, row, col)

    def _prev_month(self):
        if self.current_month == 1:
            self.current_month, self.current_year = 12, self.current_year - 1
        else:
            self.current_month -= 1
        self._render()

    def _next_month(self):
        if self.current_month == 12:
            self.current_month, self.current_year = 1, self.current_year + 1
        else:
            self.current_month += 1
        self._render()