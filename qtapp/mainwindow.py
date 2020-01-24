from PyQt5.QtWidgets import QAction, QMainWindow, QMenu

from .app import MyApp
from .keybinds import sample_keybinds, KeybindEditor, KeySequenceModel


class MainWindow(QMainWindow):
    def __init__(self, app: MyApp, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.initKeybinds()
        self.initUI()

    def initUI(self):
        self.initMenu()

        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle("Submenu")
        self.readSettings()
        
        keybind_editor = KeybindEditor(model=self.kb, parent=self)
        self.setCentralWidget(keybind_editor)
        self.show()

    def initApp(self):
        """Called on app init, both MyApp.instance() and ui are available"""
        sample_keybinds(self)

    def initKeybinds(self):
        self.kb = KeySequenceModel(parent=self)
        
    def initMenu(self):
        """Sample menubar"""
        menubar = self.menuBar()
        fileMenu = menubar.addMenu("File")

        impMenu = QMenu("Import", self)
        impAct = QAction("Import mail", self)
        impMenu.addAction(impAct)
        newAct = QAction("New", self)
        fileMenu.addAction(newAct)
        fileMenu.addMenu(impMenu)

    def readSettings(self):
        """Restores geometry and dockwidget states on startup"""
        sett = self.app.settings
        sett.beginGroup(self.__class__.__name__)
        geom = sett.value("geometry", defaultValue=None)
        if geom is not None:
            self.restoreGeometry(geom)

        state = sett.value("state", defaultValue=None)
        if state is not None:
            self.restoreState(geom)
        sett.endGroup()

    def saveSettings(self):
        """Saves geometry and dockwidget states on exit"""
        sett = self.app.settings
        sett.beginGroup(self.__class__.__name__)
        sett.setValue("geometry", self.saveGeometry())
        sett.setValue("state", self.saveState())
        sett.endGroup()

    def closeEvent(self, event):
        self.saveSettings()
        return super().closeEvent(event)
