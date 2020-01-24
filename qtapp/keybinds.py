from configparser import ConfigParser
from functools import partial
from typing import List, Union

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, QObject, Qt, pyqtSignal

# from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QKeySequenceEdit,
    QShortcut,
    QTableView,
    QVBoxLayout,
    QWidget,
)

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


class Keybind(QObject):
    """Full keybind class, includes a sequence, name, category, tooltip, plus our callbacks"""

    COLUMNS = ("text", "keysequence")
    HEADER = ("Name", "Shortcut")
    updated = pyqtSignal(object)  # emits self
    activated = pyqtSignal()

    def __init__(self, name: str, slug: str, *args, **kwargs):
        """Creates a keybind item
        
        Args:
            `name (str)`: Readable description, used in keybind editor
            `slug (str)`: used to save settings, and get from default list
        """
        super().__init__(*args, **kwargs)
        self.name = name
        self.slug = slug
        self.sequence = self.register_key(slug)

    def register_key(self, slug: str) -> Union[KeySequence, None]:
        """Register the key sequence, makes a QShortcut out of it"""
        seq = KeySequence.from_profile(slug)
        ui = MyApp.instance().ui
        self.act = QShortcut(seq, ui) if seq else QShortcut(ui)
        self.act.activated.connect(self.activated.emit)
        return seq

    @property
    def data(self) -> tuple:
        """Returns the data for our table model"""
        return (self.name, self.sequence.toString())

    def update(self, new: KeySequence):
        """Updates the keybind entry with a new keysequence and emits `updated` signal
        
        Args:
            `new (KeySequence)`: new keysequence
        """
        self.sequence.swap(new)
        self.act.setKey(self.sequence)
        self.updated.emit(self)

    def __str__(self) -> str:
        return f"Key '{self.name}': {self.sequence.toString()}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.slug}' {self.sequence.toString()}>"


class KeySequenceModel(QAbstractTableModel):
    MODEL = Keybind

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entries: List[Keybind] = []

    def register(self, kb: Keybind):
        kb.updated.connect(self.keybindUpdated)
        self.entries.append(kb)
        self.keybindUpdated(kb, row=len(self.entries) - 1)
        self.layoutChanged.emit()

    def keybindUpdated(self, keybind: Keybind, row: int = None, *args):
        """Trigger from either editing the key sequence, or when registering
        
        Args:
            keybind (Keybind): [description]
            row (int, optional): [description]. Defaults to None.
        """
        if row is None:
            try:
                row = self.entries.index(keybind)
            except ValueError:
                return
        x, y, dx, dy = (0, row, len(self.MODEL.COLUMNS), row)
        self.dataChanged.emit(self.index(x, y), self.index(dx, dy), [])

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        """Gets data"""
        if role == Qt.DisplayRole:  # Return data for the table
            return self.entries[index.row()].data[index.column()]
        elif role == Qt.UserRole:  # Return our actual model
            return self.entries[index.row()]
        return None

    def rowCount(self, parent=QModelIndex()):
        """Default implementation"""
        if parent.isValid():
            return 0
        return len(self.entries)

    def columnCount(self, parent=QModelIndex()):
        """Default implementation"""
        if parent.isValid():
            return 0
        return len(self.MODEL.COLUMNS)

    def index(self, row, column, parent=QModelIndex()):
        """Default implementation"""
        return self.createIndex(row, column, parent)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Header data"""
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.MODEL.HEADER[section]
        return None

    def getUserData(self, index: QModelIndex):
        """Returns data for Qt.Userrole of index"""
        return self.data(index, role=Qt.UserRole)

    def selectedData(self, sel: List[QModelIndex]):
        """Gets selected data, works of rows only and gets the Qt.UserRole info"""
        if not sel:
            return None
        return self.getUserData(sel[0])


class KeybindEditor(QWidget):
    def __init__(self, *args, model=None, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.kbview = view = QTableView(parent=self)
        view.setModel(model)
        view.setSortingEnabled(True)
        view.setSelectionMode(QAbstractItemView.SingleSelection)
        view.setSelectionBehavior(QAbstractItemView.SelectRows)
        view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(view)

        edit = QKeySequenceEdit(parent=self)
        edit.editingFinished.connect(partial(self.edit_finished, edit))
        layout.addWidget(edit)

        view.show()
        edit.show()

    def edit_finished(self, edit: QKeySequenceEdit, *args, **kwargs):
        sel = self.kbview.selectedIndexes()
        kb: Keybind = self.kbview.model().selectedData(sel)
        if kb:
            kb.update(edit.keySequence())


def sample_keybinds(ui):
    def triggered(*args):
        print("Triggered")

    def refresh(model, view: QTableView, *args):
        print("Refresh")
        model.dataChanged.emit(model.index(0, 0), model.index(model.columnCount(), model.rowCount()), [])

    view = ui.centralWidget().kbview
    kb = Keybind("Deselect all", "deselect")
    ui.kb.register(kb)
    kb.activated.connect(triggered)

    kb = Keybind("Refresh", "refresh")
    kb.activated.connect(partial(refresh, ui.kb, view))
    ui.kb.register(kb)

    # keybind = KeySequence.from_profile("deselect")
    # act = QAction("Test", parent=ui)
    # act.setShortcut("Ctrl+S")
    # act.setShortcutContext(Qt.ApplicationShortcut)
    # act.triggered.connect(triggered)
