from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QScrollArea, QSizePolicy, QWidget

from app.core.models.experiment import ScheduleEntry

_STEP_W  = 180
_H       = 280
_MX      = 80    # left/right margin
_BASE_Y  = 148   # y of the centre line
_DOT     = 14    # dot diameter
_LABEL_H = 68
_DATE_H  = 40


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
        self.setFixedHeight(_H + 2)
        self.setStyleSheet("background: #FFFFFF; border: none;")

        n          = len(schedule)
        total_w    = max(900, _MX * 2 + n * _STEP_W)
        today      = date.today()
        today_day  = (today - start_date).days
        total_days = schedule[-1].day_number or 1

        # proportional coordinate system: both dots and the today marker
        # map day_number → pixel so the red line always aligns with step dots
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

        # ── today marker ─────────────────────────────────────────────────
        if 0 < today_day <= total_days:
            tx = x_first + int(track_w * (today_day / total_days))
            marker = QFrame(canvas)
            marker.setGeometry(tx, _BASE_Y - 40, 1, 80)
            marker.setStyleSheet("background: #F43F5E; border: none;")
            today_lbl = _lbl("Today", canvas,
                              "color: #F43F5E; font-size: 9pt;",
                              Qt.AlignHCenter)
            today_lbl.adjustSize()
            today_lbl.move(tx - today_lbl.width() // 2, _BASE_Y + 46)

        # ── steps ────────────────────────────────────────────────────────
        for i, entry in enumerate(schedule):
            x    = x_first + int(track_w * (entry.day_number / total_days))
            done = entry.date <= today

            # dot (raised above track)
            dot = QFrame(canvas)
            dot.setFixedSize(_DOT, _DOT)
            dot.move(x - _DOT // 2, _BASE_Y - _DOT // 2 + 1)
            if done:
                dot.setStyleSheet(
                    f"background: #3B82F6; border-radius: {_DOT//2}px; border: none;")
            else:
                dot.setStyleSheet(
                    f"background: #FFFFFF; border-radius: {_DOT//2}px;"
                    " border: 2px solid #3B82F6;")
            dot.raise_()

            # step name — above baseline
            col   = "#0F172A" if done else "#94A3B8"
            wt    = "600"     if done else "400"
            name  = _lbl(entry.step.name, canvas,
                          f"color:{col}; font-size:10pt; font-weight:{wt};")
            name.setGeometry(x - _STEP_W // 2 + 6,
                             _BASE_Y - _DOT // 2 - _LABEL_H - 6,
                             _STEP_W - 12, _LABEL_H)
            name.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)

            # date + day — below baseline
            meta = _lbl(
                f"Day {entry.day_number}  ·  {entry.date.strftime('%b %d')}",
                canvas, "color: #94A3B8; font-size: 9pt;")
            meta.setGeometry(x - _STEP_W // 2 + 6,
                             _BASE_Y + _DOT // 2 + 10,
                             _STEP_W - 12, _DATE_H)
            meta.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        self.setWidget(canvas)
        self.setWidgetResizable(False)