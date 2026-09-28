from datetime import date, timedelta

from PySide6.QtCore import Qt, Signal
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

from app.core.models.experiment import ScheduleEntry
from app.core.models.protocol import Protocol


class DiffCard(QFrame):
    clicked = Signal(object)   # emits (protocol, schedule, start_date, name)

    def __init__(
        self,
        name: str,
        protocol: Protocol,
        schedule: list[ScheduleEntry],
        start_date: date,
        parent=None,
    ):
        super().__init__(parent)
        self._payload = (protocol, schedule, start_date, name)
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._set_style(hover=False)

        today = date.today()
        today_day = (today - start_date).days
        total_days = schedule[-1].day_number
        today_steps = [e for e in schedule if e.date == today]

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(10)

        # ── name + day badge ─────────────────────────────────────────────
        top = QHBoxLayout()
        name_lbl = QLabel(name)
        nf = QFont()
        nf.setPointSize(13)
        nf.setBold(True)
        name_lbl.setFont(nf)
        name_lbl.setStyleSheet("color:#0F172A;")

        day_badge = QLabel(f"Day {max(today_day, 0)}")
        day_badge.setStyleSheet(
            "background:#EFF6FF; color:#2563EB; border-radius:4px;"
            " padding:2px 8px; font-size:9pt; font-weight:600;"
        )
        top.addWidget(name_lbl)
        top.addStretch()
        top.addWidget(day_badge)
        root.addLayout(top)

        # ── protocol name ────────────────────────────────────────────────
        proto_lbl = QLabel(protocol.name)
        proto_lbl.setStyleSheet("color:#94A3B8; font-size:10pt;")
        root.addWidget(proto_lbl)

        # ── progress bar ─────────────────────────────────────────────────
        progress = QProgressBar()
        progress.setRange(0, total_days)
        progress.setValue(max(min(today_day, total_days), 0))
        progress.setTextVisible(False)
        progress.setFixedHeight(5)
        progress.setStyleSheet("""
            QProgressBar {
                background: #E2E8F0;
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: #3B82F6;
                border-radius: 3px;
            }
        """)
        root.addWidget(progress)

        prog_lbl = QLabel(f"{max(today_day, 0)} of {total_days} days")
        prog_lbl.setStyleSheet("color:#CBD5E1; font-size:9pt;")
        root.addWidget(prog_lbl)

        # ── today's steps ────────────────────────────────────────────────
        if today_steps:
            div = QWidget()
            div.setFixedHeight(1)
            div.setStyleSheet("background:#F1F5F9;")
            root.addWidget(div)

            today_hdr = QLabel("TODAY")
            today_hdr.setStyleSheet(
                "color:#3B82F6; font-size:8pt; font-weight:700; letter-spacing:1px;"
            )
            root.addWidget(today_hdr)

            for e in today_steps:
                step_lbl = QLabel(e.step.name)
                step_lbl.setStyleSheet("color:#0F172A; font-size:10pt;")
                root.addWidget(step_lbl)
        else:
            no_step = QLabel("No steps today")
            no_step.setStyleSheet("color:#CBD5E1; font-size:10pt;")
            root.addWidget(no_step)

        # ── footer ───────────────────────────────────────────────────────
        div2 = QWidget()
        div2.setFixedHeight(1)
        div2.setStyleSheet("background:#F1F5F9;")
        root.addWidget(div2)

        footer = QHBoxLayout()
        date_lbl = QLabel(f"Started {start_date.strftime('%b %d, %Y')}")
        date_lbl.setStyleSheet("color:#CBD5E1; font-size:9pt;")
        arrow = QLabel("→")
        arrow.setStyleSheet("color:#CBD5E1; font-size:11pt;")
        footer.addWidget(date_lbl)
        footer.addStretch()
        footer.addWidget(arrow)
        root.addLayout(footer)

    def _set_style(self, hover: bool):
        border = "#3B82F6" if hover else "#E2E8F0"
        self.setStyleSheet(
            f"QFrame {{ background:#FFFFFF; border:1px solid {border};"
            " border-radius:12px; }}"
        )

    def enterEvent(self, e):
        self._set_style(hover=True)
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._set_style(hover=False)
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit(self._payload)
        super().mousePressEvent(e)


class DashboardView(QWidget):
    open_diff = Signal(object)   # emits (protocol, schedule, start_date, name)
    new_diff  = Signal()

    def __init__(self, protocol: Protocol, mock_diffs: list[dict], parent=None):
        super().__init__(parent)
        self._protocol = protocol
        self._mock_diffs = mock_diffs

        root = QVBoxLayout(self)
        root.setContentsMargins(40, 32, 40, 32)
        root.setSpacing(0)

        # ── header ───────────────────────────────────────────────────────
        header = QHBoxLayout()

        title = QLabel("Diff Tracker")
        tf = QFont()
        tf.setPointSize(22)
        tf.setBold(True)
        title.setFont(tf)
        title.setStyleSheet("color:#0F172A;")

        new_btn = QPushButton("+ New Diff")
        new_btn.setFixedHeight(38)
        new_btn.setCursor(Qt.PointingHandCursor)
        new_btn.setStyleSheet("""
            QPushButton {
                background: #3B82F6;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 0 20px;
                font-size: 11pt;
                font-weight: 600;
            }
            QPushButton:hover { background: #2563EB; }
        """)
        new_btn.clicked.connect(self.new_diff)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(new_btn)
        root.addLayout(header)
        root.addSpacing(6)

        subtitle = QLabel(f"{len(mock_diffs)} active differentiation{'s' if len(mock_diffs) != 1 else ''}")
        subtitle.setStyleSheet("color:#94A3B8; font-size:11pt;")
        root.addWidget(subtitle)
        root.addSpacing(28)

        # ── card grid in scroll area ──────────────────────────────────────
        scroll = QScrollArea()
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        grid = QVBoxLayout(container)
        grid.setSpacing(16)
        grid.setContentsMargins(0, 0, 0, 0)

        for d in mock_diffs:
            card = DiffCard(
                name=d["name"],
                protocol=d["protocol"],
                schedule=d["schedule"],
                start_date=d["start_date"],
            )
            card.clicked.connect(self.open_diff)
            grid.addWidget(card)

        grid.addStretch()
        scroll.setWidget(container)
        root.addWidget(scroll, 1)
