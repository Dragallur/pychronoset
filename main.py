import typing
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QVBoxLayout, QWidget, QBoxLayout
import sys
import json
import workout_bar as WB

def load_config(file_path):
    with open(file_path, 'r') as f:
        config_data = json.load(f)
    return config_data

class MainWindow(QWidget):
    def __init__(self, config_data):
        super().__init__()
        main_window_x = int(config_data['main_window']['x_percent'] * screen_width)
        main_window_y = int(config_data['main_window']['y_percent'] * screen_height)
        main_window_width = int(config_data['main_window']['width_percent'] * screen_width)
        main_window_height = int(config_data['main_window']['height_percent'] * screen_height)

        self.setWindowTitle("PyChronoSet")
        self.setGeometry(main_window_x, main_window_y, main_window_width, main_window_height)

        self.setAcceptDrops(True)

        self.progress_bar = WB.CustomProgressBar(self, config_data['progress_bar'])
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.progress_bar)
        self.progress_bar.show()

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        position = event.pos()
        self.move(position)

        event.setDropAction(QtCore.Qt.MoveAction)
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = QDesktopWidget().screenGeometry()
    screen_width, screen_height = screen.width(), screen.height()
    config_data = load_config('config.json')
    
    main_window = MainWindow(config_data)
    
    main_window.show()
    sys.exit(app.exec_())