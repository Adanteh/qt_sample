import sys
from .app import MyApp
from .mainwindow import MainWindow


def start(arg=None):
    if arg is None:
        arg = sys.argv
    app = MyApp(arg)
    app.ui = MainWindow(app)
    app.ui.initApp()

    sys.exit(app.exec_())
