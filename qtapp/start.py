import sys
from .app import MyApp
from .mainwindow import MainWindow


def start(arg=None):
    if arg is None:
        arg = sys.argv
    app = MyApp(arg)
    _ = MainWindow(app)
    sys.exit(app.exec_())
