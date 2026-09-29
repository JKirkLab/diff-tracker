from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

_WELL_SIZE = 100
_WELLS = [
    ("A1", 0, 0), ("A2", 0, 1), ("A3", 0, 2),
    ("B1", 1, 0), ("B2", 1, 1), ("B3", 1, 2),
]

_STYLE = """
QDialog { background: #FFFFFF; }
QLabel  { color: #0F172A; border: none; }
QLineEdit {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 4px 8px;
    color: #0F172A;
    font-size: 10pt;
}
QLineEdit:focus { border: 1px solid #3B82F6; background: #FFFFFF; }
QTabWidget::pane {
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    background: #FFFFFF;
}
QTabBar::tab {
    background: #F8FAFC;
    color: #64748B;
    border: 1px solid #E2E8F0;
    border-bottom: none;
    border-radius: 6px 6px 0 0;
    padding: 6px 16px;
    font-size: 10pt;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #FFFFFF;
    color: #0F172A;
    font-weight: 600;
    border-bottom: 1px solid #FFFFFF;
}
QTabBar::tab:hover:!selected { background: #F1F5F9; }
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
QPushButton#add_plate {
    background: transparent; color: #3B82F6;
    border: 1px dashed #93C5FD; border-radius: 6px;
    padding: 4px 12px; font-size: 9pt;
}
QPushButton#add_plate:hover { background: #EFF6FF; }
"""


class _WellWidget(QWidget):
    def __init__(self, well_id: str, note: str = "", parent=None):
        super().__init__(parent)
        self._well_id = well_id

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignHCenter)

        circle = QFrame()
        circle.setFixedSize(_WELL_SIZE, _WELL_SIZE)
        circle.setStyleSheet(
            f"background: #F1F5F9; border: 2px solid #CBD5E1;"
            f" border-radius: {_WELL_SIZE // 2}px;"
        )
        circle.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        id_lbl = QLabel(well_id, circle)
        f = QFont()
        f.setPointSize(14)
        f.setBold(True)
        id_lbl.setFont(f)
        id_lbl.setStyleSheet("color: #64748B; border: none; background: transparent;")
        id_lbl.setAlignment(Qt.AlignCenter)
        id_lbl.setGeometry(0, 0, _WELL_SIZE, _WELL_SIZE)

        layout.addWidget(circle, 0, Qt.AlignHCenter)

        self._note_edit = QLineEdit(note)
        self._note_edit.setPlaceholderText("Add note...")
        self._note_edit.setFixedWidth(_WELL_SIZE + 16)
        layout.addWidget(self._note_edit, 0, Qt.AlignHCenter)

    def note(self) -> str:
        return self._note_edit.text().strip()

    def well_id(self) -> str:
        return self._well_id


class _PlateTab(QWidget):
    def __init__(self, notes: dict[str, str] | None = None, parent=None):
        super().__init__(parent)
        notes = notes or {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(0)

        grid = QGridLayout()
        grid.setSpacing(16)

        self._wells: list[_WellWidget] = []
        for well_id, row, col in _WELLS:
            well = _WellWidget(well_id, notes.get(well_id, ""))
            self._wells.append(well)
            grid.addWidget(well, row, col, Qt.AlignHCenter)

        layout.addLayout(grid)

    def well_notes(self) -> dict[str, str]:
        return {w.well_id(): w.note() for w in self._wells}


class WellPlateDialog(QDialog):
    def __init__(self, diff: dict, existing_plates: list[dict[str, str]] | None = None, parent=None):
        """
        existing_plates: list of {well_id: note} dicts, one per plate.
        """
        super().__init__(parent)
        self.setWindowTitle(f"Well Plates — {diff['name']}")
        self.setMinimumWidth(520)
        self.setMinimumHeight(420)
        self.setStyleSheet(_STYLE)

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        # header
        title = QLabel(diff["name"])
        tf = QFont()
        tf.setPointSize(15)
        tf.setBold(True)
        title.setFont(tf)
        root.addWidget(title)

        sub = QLabel("Each tab is a separate 6-well plate. Click into any field to annotate.")
        sub.setStyleSheet("color: #94A3B8; font-size: 10pt; border: none;")
        root.addWidget(sub)

        div = QWidget()
        div.setFixedHeight(1)
        div.setStyleSheet("background: #E2E8F0;")
        root.addWidget(div)

        # tab bar row with "+ Add Plate" button
        tab_hdr = QHBoxLayout()
        self._tabs = QTabWidget()
        self._tabs.setTabsClosable(True)
        self._tabs.tabCloseRequested.connect(self._remove_plate)
        tab_hdr.addWidget(self._tabs, 1)

        add_btn = QPushButton("+ Add Plate")
        add_btn.setObjectName("add_plate")
        add_btn.setFixedHeight(28)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._add_plate)
        tab_hdr.addWidget(add_btn, 0, Qt.AlignBottom)

        root.addLayout(tab_hdr, 1)

        # populate existing plates or start with one
        self._plate_tabs: list[_PlateTab] = []
        for notes in (existing_plates or [{}]):
            self._add_plate(notes)

        div2 = QWidget()
        div2.setFixedHeight(1)
        div2.setStyleSheet("background: #E2E8F0;")
        root.addWidget(div2)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        cancel = QPushButton("Cancel")
        cancel.setObjectName("cancel")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Save")
        save.setObjectName("save")
        save.clicked.connect(self.accept)
        btn_row.addWidget(cancel)
        btn_row.addWidget(save)
        root.addLayout(btn_row)

    def _add_plate(self, notes: dict[str, str] | None = None):
        if isinstance(notes, bool):
            notes = {}
        plate = _PlateTab(notes or {})
        self._plate_tabs.append(plate)
        idx = self._tabs.addTab(plate, f"Plate {len(self._plate_tabs)}")
        self._tabs.setCurrentIndex(idx)

    def _remove_plate(self, idx: int):
        if self._tabs.count() <= 1:
            return  # always keep at least one plate
        self._tabs.removeTab(idx)
        del self._plate_tabs[idx]
        # relabel remaining tabs
        for i in range(self._tabs.count()):
            self._tabs.setTabText(i, f"Plate {i + 1}")

    def all_plates(self) -> list[dict[str, str]]:
        """Returns [{well_id: note}, ...] one dict per plate."""
        return [t.well_notes() for t in self._plate_tabs]
