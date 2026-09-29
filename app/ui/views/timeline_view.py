from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QScrollArea, QSizePolicy, QWidget

from app.core.models.experiment import ScheduleEntry

_STEP_W  = 200
_H       = 420
_MX      = 80
_BASE_Y  = 190
_DOT     = 16
_NAME_H  = 44
_DATE_H  = 26
_DESC_H  = 36


def _lbl(text: str, parent: QWidget, style: str, align=Qt.AlignHCenter) -> QLabel:
    w = QLabel(text, parent)
    w.setWordWrap(True)
    w.setAlignment(align)
    w.setStyleSheet(style)
    return w


class TimelineView(QScrollArea):
    def __init__(self, schedule: list[ScheduleEntry], start_date: date, parent=None):
        super().__init__(parent)
        self.setFrameShape(QScrollArea.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(_H + 4)
        self.setStyleSheet("background: #FFFFFF; border: none;")

        n          = len(schedule)
        total_w    = max(900, _MX * 2 + n * _STEP_W)
        today      = date.today()
        today_day  = (today - start_date).days
        total_days = schedule[-1].day_number or 1

        x_first = _MX
        x_last  = total_w - _MX
        track_w = x_last - x_first

        canvas = QWidget()
        canvas.setFixedSize(total_w, _H)
        canvas.setStyleSheet("background: #FFFFFF;")

        # ── track ────────────────────────────────────────────────────────
        track = QFrame(canvas)
        track.setGeometry(x_first, _BASE_Y, track_w, 2)
        track.setStyleSheet("background: #E2E8F0; border: none;")

        # ── progress fill ────────────────────────────────────────────────
        if today_day > 0:
            fill_w = int(track_w * min(today_day / total_days, 1.0))
            fill = QFrame(canvas)
            fill.setGeometry(x_first, _BASE_Y, fill_w, 2)
            fill.setStyleSheet("background: #3B82F6; border: none;")

        # ── steps ─────────────────────────────────────────────────────────
        # Even steps: desc → name → date stacked ABOVE the track
        # Odd  steps: date → name → desc stacked BELOW the track
        # The two rows occupy completely separate vertical regions.
        GAP = 3
        dot_top = _BASE_Y - _DOT // 2

        for i, entry in enumerate(schedule):
            x    = x_first + int(track_w * (entry.day_number / total_days))
            done = entry.date <= today

            col      = "#0F172A" if done else "#94A3B8"
            wt       = "600"     if done else "400"
            desc_col = "#64748B" if done else "#CBD5E1"
            lw       = _STEP_W - 12
            lx       = max(0, min(x - lw // 2, total_w - lw))

            if i % 2 == 0:
                # stack upward from just above the dot
                date_y = dot_top - GAP - _DATE_H
                name_y = date_y - GAP - _NAME_H
                desc_y = name_y - GAP - _DESC_H
                align  = Qt.AlignBottom | Qt.AlignHCenter
            else:
                # stack downward from just below the dot
                dot_bot = _BASE_Y + _DOT // 2
                date_y  = dot_bot + GAP
                name_y  = date_y + _DATE_H + GAP
                desc_y  = name_y + _NAME_H + GAP
                align   = Qt.AlignTop | Qt.AlignHCenter

            date_lbl = _lbl(
                f"Day {entry.day_number}  ·  {entry.date.strftime('%b %d')}",
                canvas, "color: #94A3B8; font-size: 10pt;")
            date_lbl.setGeometry(lx, date_y, lw, _DATE_H)
            date_lbl.setAlignment(align)

            name_lbl = _lbl(entry.step.name, canvas,
                             f"color:{col}; font-size:11pt; font-weight:{wt};")
            name_lbl.setGeometry(lx, name_y, lw, _NAME_H)
            name_lbl.setAlignment(align)
            if entry.step.description:
                name_lbl.setToolTip(entry.step.description)

            if entry.step.description:
                desc_lbl = _lbl(entry.step.description, canvas,
                                 f"color:{desc_col}; font-size:9pt;")
                desc_lbl.setGeometry(lx, desc_y, lw, _DESC_H)
                desc_lbl.setAlignment(align)

            dot = QFrame(canvas)
            dot.setFixedSize(_DOT, _DOT)
            dot.move(x - _DOT // 2, dot_top)
            if done:
                dot.setStyleSheet(
                    f"background: #3B82F6; border-radius: {_DOT//2}px; border: none;")
            else:
                dot.setStyleSheet(
                    f"background: #FFFFFF; border-radius: {_DOT//2}px;"
                    " border: 2px solid #3B82F6;")
            dot.raise_()

        # ── today marker (last so it renders over step labels) ────────────
        # The marker runs from above the track to near the canvas bottom,
        # and the "Today" label sits at the very bottom — always clear of
        # step labels regardless of which row they occupy.
        if 0 < today_day <= total_days:
            tx         = x_first + int(track_w * (today_day / total_days))
            lbl_h      = 16
            marker_top = _BASE_Y - 40
            lbl_y      = _H - lbl_h - 4
            marker     = QFrame(canvas)
            marker.setGeometry(tx, marker_top, 1, lbl_y - marker_top)
            marker.setStyleSheet("background: #F43F5E; border: none;")
            marker.raise_()
            today_lbl = _lbl("Today", canvas,
                              "color: #F43F5E; font-size: 9pt;",
                              Qt.AlignHCenter)
            today_lbl.adjustSize()
            today_lbl.move(tx - today_lbl.width() // 2, lbl_y)
            today_lbl.raise_()

        self.setWidget(canvas)
        self.setWidgetResizable(False)
