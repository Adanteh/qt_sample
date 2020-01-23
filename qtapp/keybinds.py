from typing import List
from configparser import ConfigParser
from functools import partial

# from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut, QKeySequenceEdit, QWidget, QTableView, QVBoxLayout, QDialog, QHeaderView, QAbstractItemView
from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, pyqtSignal, pyqtSlot

# from PyQt5.QtCore import tr

from . import FOLDER
from .app import MyApp


def load_default_keybinds():
    parser = ConfigParser()
    parser.read(FOLDER / "keybinds.shortcut")
    return parser["keybinds"]


DEFAULT_KEYBINDS = load_default_keybinds()


class UnknownKeybind(Exception):
    pass


class KeySequence(QKeySequence):
    """KeySequence represents which buttons we press to trigger an action"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_arma(self):
        """Returns arma style keybind from this sequence"""

    @classmethod
    def from_arma(cls, keybind) -> "KeySequence":
        """Turns Arma3 keybind tuple into QKeySequence-like"""
        return cls(keybind)

    @classmethod
    def from_profile(cls, name: str) -> "KeySequence":
        """Creates keysequence from reading a name out of profile, or getting default from saved file"""
        sett = MyApp.instance().settings
        keybind = sett.value(f"keybinds/{name}", defaultValue=None)
        if not keybind:
            try:
                keybind = DEFAULT_KEYBINDS[name]
            except KeyError as e:
                raise UnknownKeybind(e)
        return cls(keybind)


class Keybind:
    """Full keybind class, includes a sequence, name, category, tooltip, plus our callbacks"""

    COLUMNS = ("text", "keysequence")
    HEADER = ("Name", "Shortcut")

    def __init__(self, name: str, slug: str, *args, **kwargs):
        """Creates a keybind item
        
        Args:
            name (str): Readable description, used in keybind editor
            slug (str): used to save settings, and get from default list
        """
        self.name = name
        self.sequence = KeySequence.from_profile(slug)
        self.register()

    @property
    def data(self) -> tuple:
        """Returns the data for our table model"""
        return (self.name, self.sequence.toString())

    def register(self):
        pass


class KeySequenceModel(QAbstractTableModel):
    MODEL = Keybind

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entries: List[Keybind] = []
        self.loadData()

    def register(self, kb: Keybind):
        self.entries.append(kb)
        x, y, dx, dy = (0, len(self.entries), len(self.MODEL.COLUMNS), len(self.entries))
        self.dataChanged.emit(self.index(x, y), self.index(dx, dy))

    def loadData(self):
        for action in self.entries:
            self.entries.append(action)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self.entries[index.row()].data[index.column()]
        return None

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.entries)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.MODEL.COLUMNS)

    def index(self, row, column, parent=QModelIndex()):
        return self.createIndex(row, column, parent)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.MODEL.HEADER[section]
        return None


class KeybindEditor(QWidget):
    def __init__(self, *args, model=None, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QVBoxLayout()
        self.setLayout(layout)

        view = QTableView(parent=self)
        view.setModel(model)
        view.setSortingEnabled(True)
        view.setSelectionMode(QAbstractItemView.SingleSelection)
        view.setSelectionBehavior(QAbstractItemView.SelectRows)

        view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(view)

        edit = QKeySequenceEdit(parent=self)
        edit.editingFinished.connect(self.edit_finished)
        layout.addWidget(edit)

        view.show()
        edit.show()

    def edit_finished(self, *args, **kwargs):
        pass


def sample_keybinds(ui):
    def triggered(*args):
        print("Triggered")

    def refresh(model, *args):
        print("Refresh")

    kb = Keybind("Deselect all", "deselect")
    act = QShortcut(kb.sequence, ui)
    act.activated.connect(triggered)
    ui.kb.register(kb)

    kb = Keybind("Refresh", "refresh")
    act = QShortcut(kb.sequence, ui)
    act.activated.connect(partial(refresh, ui.kb))
    ui.kb.register(kb)

    # keybind = KeySequence.from_profile("deselect")
    # act = QAction("Test", parent=ui)
    # act.setShortcut("Ctrl+S")
    # act.setShortcutContext(Qt.ApplicationShortcut)
    # act.triggered.connect(triggered)
