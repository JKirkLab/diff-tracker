from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.ui.views.timeline_view import TimelineView

DIFF_COLORS = ["#2563EB", "#059669", "#D97706", "#7C3AED", "#DC2626"]


class CollapsibleDiffItem(QFrame):
    def __init__(self, diff: dict, color: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            "QFrame { background:#FFFFFF; border:1px solid #E2E8F0;"
            " border-radius:10px; }"
        )
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        today      = date.today()
        today_day  = (today - diff["start_date"]).days
        total_days = diff["schedule"][-1].day_number
        today_steps = [e for e in diff["schedule"] if e.date == today]

        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(16, 12, 16, 12)
        self._root.setSpacing(8)

        # ── header (always visible) ───────────────────────────────────────
        header = QHBoxLayout()
        header.setSpacing(10)

        self._arrow = QLabel("▶")
        self._arrow.setStyleSheet(f"color:{color}; font-size:10pt;")
        self._arrow.setFixedWidth(16)

        name_lbl = QLabel(diff["name"])
        nf = QFont()
        nf.setPointSize(11)
        nf.setBold(True)
        name_lbl.setFont(nf)
        name_lbl.setStyleSheet("color:#0F172A; border:none;")

        day_badge = QLabel(f"Day {max(today_day, 0)}")
        day_badge.setStyleSheet(
            f"background:#F8FAFC; color:{color}; border:1px solid {color};"
            " border-radius:4px; padding:1px 8px; font-size:8pt; font-weight:600;"
        )

        header.addWidget(self._arrow)
        header.addWidget(name_lbl)
        header.addStretch()
        header.addWidget(day_badge)
        self._root.addLayout(header)

        # ── progress ──────────────────────────────────────────────────────
        pb = QProgressBar()
        pb.setRange(0, total_days)
        pb.setValue(max(min(today_day, total_days), 0))
        pb.setTextVisible(False)
        pb.setFixedHeight(4)
        pb.setStyleSheet(f"""
            QProgressBar {{ background:#E2E8F0; border:none; border-radius:2px; }}
            QProgressBar::chunk {{ background:{color}; border-radius:2px; }}
        """)
        self._root.addWidget(pb)

        # ── today's steps ─────────────────────────────────────────────────
        if today_steps:
            for e in today_steps:
                row = QHBoxLayout()
                dot = QFrame()
                dot.setFixedSize(6, 6)
                dot.setStyleSheet(
                    f"background:{color}; border-radius:3px;"
                )
                dot.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                lbl = QLabel(e.step.name)
                lbl.setStyleSheet("color:#475569; font-size:9pt; border:none;")
                row.addWidget(dot, 0, Qt.AlignVCenter)
                row.addWidget(lbl)
                row.addStretch()
                self._root.addLayout(row)
        else:
            no = QLabel("No steps today")
            no.setStyleSheet("color:#CBD5E1; font-size:9pt; border:none;")
            self._root.addWidget(no)

        # ── collapsible timeline ──────────────────────────────────────────
        self._timeline_wrapper = QWidget()
        self._timeline_wrapper.setStyleSheet("border:none;")
        tw_layout = QVBoxLayout(self._timeline_wrapper)
        tw_layout.setContentsMargins(0, 8, 0, 0)
        tw_layout.setSpacing(0)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet("background:#E2E8F0; border:none;")
        tw_layout.addWidget(sep)

        timeline = TimelineView(diff["schedule"], diff["start_date"])
        tw_layout.addWidget(timeline)

        self._timeline_wrapper.setVisible(False)
        self._root.addWidget(self._timeline_wrapper)

        self._expanded = False

        # make header clickable
        for widget in [self._arrow, name_lbl]:
            widget.mousePressEvent = lambda _e: self._toggle()
        self.mousePressEvent = lambda _e: self._toggle()

    def _toggle(self):
        self._expanded = not self._expanded
        self._arrow.setText("▼" if self._expanded else "▶")
        self._timeline_wrapper.setVisible(self._expanded)
        # tell parent to recalculate size
        self.updateGeometry()
        if self.parent():
            self.parent().adjustSize()


class DiffListPanel(QWidget):
    def __init__(self, diffs: list[dict], parent=None):
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # header
        hdr = QHBoxLayout()
        hdr.setContentsMargins(4, 0, 4, 12)
        title = QLabel("Active Diffs")
        tf = QFont()
        tf.setPointSize(13)
        tf.setBold(True)
        title.setFont(tf)
        title.setStyleSheet("color:#0F172A;")
        count = QLabel(f"{len(diffs)}")
        count.setStyleSheet(
            "background:#E2E8F0; color:#64748B; border-radius:10px;"
            " padding:1px 8px; font-size:9pt; font-weight:600;"
        )
        hdr.addWidget(title)
        hdr.addSpacing(8)
        hdr.addWidget(count)
        hdr.addStretch()
        root.addLayout(hdr)

        # scrollable list
        scroll = QScrollArea()
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(4, 0, 4, 0)
        vbox.setSpacing(10)

        for i, diff in enumerate(diffs):
            color = DIFF_COLORS[i % len(DIFF_COLORS)]
            item = CollapsibleDiffItem(diff, color)
            vbox.addWidget(item)

        vbox.addStretch()
        scroll.setWidget(container)
        root.addWidget(scroll, 1)