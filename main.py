import typing
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QVBoxLayout, QWidget, QBoxLayout
import sys
import json
import workout_bar as WB
import numpy as np

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
        segment = event.source()
        orig_seg_y = int(segment.y())
        ind_org = self.progress_bar.segments.index(segment)
        temp = np.argwhere(position.x() > segment.parentWidget().seg_x_pos + self.progress_bar.progress_bar_rect.x())

        if temp.size == 0:
            ind_new = 0
        else:
            ind_new = temp[-1][0]
            
        old_order = list(range(len(self.progress_bar.segments)))
        new_order = old_order
        new_order.pop(ind_org)
        new_order.insert(ind_new, ind_org)
        self.progress_bar.segments = [self.progress_bar.segments[i] for i in new_order]

        for i in range(min(ind_org, ind_new), max(ind_org, ind_new)+1):
            if i == 0:
                self.progress_bar.seg_x_pos[i] = 0
            else:
                self.progress_bar.seg_x_pos[i] = self.progress_bar.seg_x_pos[i-1] + self.progress_bar.segments[i-1].segment_width
            self.progress_bar.segments[i].move(int(self.progress_bar.seg_x_pos[i] + self.progress_bar.progress_bar_rect.x()), orig_seg_y)

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