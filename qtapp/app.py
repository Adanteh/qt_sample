from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication

from . import FOLDER


class MyApp(QApplication):
    def __init__(self, argv, Liststr=None):
        QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, str(FOLDER.parent / "settings"))
        self.settings = QSettings(QSettings.IniFormat, QSettings.UserScope, "adanteh", "testapp")
        self.settings.IniFormat
        super().__init__(argv)

    @staticmethod
    def instance(*args, **kwargs) -> "MyApp":
        return QApplication.instance()
