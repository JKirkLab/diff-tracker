import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from app.core.protocols.loader import load_protocol
from app.core.utils.schedule import compute_schedule
from app.ui.dialogs.start_dialog import StartDiffDialog
from app.ui.views.calendar_view import CalendarView


class MainWindow(QMainWindow):
    def __init__(self, protocol, schedule, start_date):
        super().__init__()
        self.setWindowTitle("Diff Tracker")
        self.setMinimumSize(1000, 680)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(20, 16, 20, 20)
        root.setSpacing(12)

        # Title row
        title_row = QHBoxLayout()
        name_lbl = QLabel(protocol.name)
        f = QFont()
        f.setPointSize(16)
        f.setBold(True)
        name_lbl.setFont(f)

        meta_lbl = QLabel(
            f"Started {start_date.strftime('%B %d, %Y')}  ·  {len(schedule)} steps  ·  "
            f"Day 0 → Day {schedule[-1].day_number}"
        )
        meta_lbl.setStyleSheet("color: #64748B;")

        title_row.addWidget(name_lbl)
        title_row.addStretch()
        title_row.addWidget(meta_lbl)
        root.addLayout(title_row)

        line = QWidget()
        line.setFixedHeight(1)
        line.setStyleSheet("background: #E2E8F0;")
        root.addWidget(line)

        root.addWidget(CalendarView(schedule, start_date), 1)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Inter", 10))

    protocol = load_protocol("allen")

    dialog = StartDiffDialog(protocol.name)
    if dialog.exec() != QDialog.Accepted:
        sys.exit(0)

    start_date = dialog.start_date()
    schedule = compute_schedule(protocol, start_date)

    window = MainWindow(protocol, schedule, start_date)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()