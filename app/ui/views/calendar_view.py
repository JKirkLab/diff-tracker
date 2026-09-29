from datetime import date

from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QColor, QFont, QTextCharFormat
from PySide6.QtWidgets import (
    QCalendarWidget,
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.core.models.experiment import ScheduleEntry

# step highlight: modern orange
_STEP_BG      = "#FFEDD5"
_STEP_FG      = "#EA580C"
_STEP_BG_BUSY = "#FED7AA"   # 2+ diffs on same day — slightly deeper
_STEP_FG_BUSY = "#C2410C"

DIFF_COLORS = ["#2563EB", "#059669", "#D97706", "#7C3AED", "#DC2626"]


class CalendarView(QWidget):
    """
    Unified calendar across all active diffs.
    diffs: list of {"name": str, "schedule": list[ScheduleEntry]}
    """

    def __init__(self, diffs: list[dict], parent=None):
        super().__init__(parent)

        # date → list of (diff_name, diff_color_fg, entry)
        self._index: dict[date, list[tuple[str, str, ScheduleEntry]]] = {}
        for i, diff in enumerate(diffs):
            fg = DIFF_COLORS[i % len(DIFF_COLORS)]
            for entry in diff["schedule"]:
                self._index.setdefault(entry.date, []).append(
                    (diff["name"], fg, entry)
                )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # ── calendar widget ───────────────────────────────────────────────
        self._cal = QCalendarWidget()
        self._cal.setGridVisible(True)
        self._cal.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self._cal.setFirstDayOfWeek(Qt.Monday)
        self._cal.setStyleSheet("""
            QCalendarWidget QAbstractItemView {
                background: #FFFFFF;
                color: #0F172A;
                selection-background-color: #3B82F6;
                selection-color: #FFFFFF;
                font-size: 13pt;
                outline: none;
                gridline-color: #E2E8F0;
            }
            QCalendarWidget QAbstractItemView:disabled { color: #CBD5E1; }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background: #FFFFFF;
                padding: 6px 4px;
            }
            QCalendarWidget QToolButton {
                color: #0F172A;
                background: transparent;
                font-size: 15pt;
                font-weight: 600;
                border: none;
                border-radius: 6px;
                padding: 4px 10px;
            }
            QCalendarWidget QToolButton:hover { background: #F1F5F9; }
            QCalendarWidget QToolButton::menu-indicator { image: none; width: 0; }
            QCalendarWidget QMenu {
                background: #FFFFFF;
                color: #0F172A;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
            }
            QCalendarWidget QSpinBox {
                color: #0F172A;
                background: #FFFFFF;
                border: none;
                font-size: 15pt;
            }
        """)

        # remove default red weekends
        plain = QTextCharFormat()
        plain.setForeground(QColor("#0F172A"))
        self._cal.setWeekdayTextFormat(Qt.Saturday, plain)
        self._cal.setWeekdayTextFormat(Qt.Sunday, plain)

        # highlight step dates in orange; busier dates get slightly deeper
        for d, entries in self._index.items():
            fmt = QTextCharFormat()
            if len(entries) == 1:
                fmt.setBackground(QColor(_STEP_BG))
                fmt.setForeground(QColor(_STEP_FG))
            else:
                fmt.setBackground(QColor(_STEP_BG_BUSY))
                fmt.setForeground(QColor(_STEP_FG_BUSY))
            fmt.setFontWeight(700)
            self._cal.setDateTextFormat(QDate(d.year, d.month, d.day), fmt)

        layout.addWidget(self._cal)

        # ── detail panel ─────────────────────────────────────────────────
        self._detail_scroll = QScrollArea()
        self._detail_scroll.setFrameShape(QScrollArea.NoFrame)
        self._detail_scroll.setWidgetResizable(True)
        self._detail_scroll.setFixedHeight(180)
        self._detail_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._detail_scroll.setStyleSheet(
            "background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px;"
        )

        self._detail_widget = QWidget()
        self._detail_widget.setStyleSheet("background: transparent;")
        self._detail_layout = QVBoxLayout(self._detail_widget)
        self._detail_layout.setContentsMargins(14, 12, 14, 12)
        self._detail_layout.setSpacing(8)
        self._detail_scroll.setWidget(self._detail_widget)
        layout.addWidget(self._detail_scroll)

        self._cal.selectionChanged.connect(self._on_select)
        self._cal.setSelectedDate(QDate.currentDate())
        self._on_select()

    def _clear_detail(self):
        while self._detail_layout.count():
            item = self._detail_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _on_select(self):
        self._clear_detail()
        qd = self._cal.selectedDate()
        d = date(qd.year(), qd.month(), qd.day())
        entries = self._index.get(d)

        if not entries:
            lbl = QLabel("No steps scheduled — select a highlighted date to see what's due.")
            lbl.setStyleSheet("color: #CBD5E1; font-size: 10pt;")
            self._detail_layout.addWidget(lbl)
            return

        date_hdr = QLabel(d.strftime("%B %d, %Y"))
        f = QFont()
        f.setPointSize(13)
        f.setBold(True)
        date_hdr.setFont(f)
        date_hdr.setStyleSheet("color: #0F172A; border: none;")
        self._detail_layout.addWidget(date_hdr)

        for diff_name, fg, entry in entries:
            block = QVBoxLayout()
            block.setSpacing(2)

            row = QHBoxLayout()
            row.setSpacing(10)

            dot = QFrame()
            dot.setFixedSize(8, 8)
            dot.setStyleSheet(f"background:{fg}; border-radius:4px; border:none;")
            dot.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

            name_lbl = QLabel(f"<b>{diff_name}</b>  ·  Day {entry.day_number}  ·  {entry.step.name}")
            name_lbl.setStyleSheet("color: #0F172A; font-size: 12pt; border: none;")

            row.addWidget(dot, 0, Qt.AlignVCenter)
            row.addWidget(name_lbl)
            row.addStretch()
            block.addLayout(row)

            if entry.step.description:
                desc_lbl = QLabel(entry.step.description)
                desc_lbl.setStyleSheet("color: #64748B; font-size: 11pt; padding-left: 18px; border: none;")
                desc_lbl.setWordWrap(True)
                block.addWidget(desc_lbl)

            wrapper = QWidget()
            wrapper.setStyleSheet("background: transparent; border: none;")
            wrapper.setLayout(block)
            self._detail_layout.addWidget(wrapper)

        self._detail_layout.addStretch()
