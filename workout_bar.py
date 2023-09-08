import sys
import json
import time
from PyQt5.QtCore import QTimer, Qt, QPoint, QSize
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout

class CustomProgressBar(QWidget):
    total_duration = 0
    total_elapsed_time = 0
    elapsed_time = 0
    current_segment = 0

    def __init__(self, parent, progress_bar_size):
        super().__init__(parent)
        self.segments = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timer_event)
        self.timer_interval = 50  # milliseconds
        self.progress_bar_size = progress_bar_size
        self.progress_bar_rect = self.rect()
        self.progress_bar_rect.setX(self.parentWidget().width() * self.progress_bar_size["x_percent"])
        self.progress_bar_rect.setY(self.parentWidget().height() * self.progress_bar_size["y_percent"])
        self.progress_bar_rect.setWidth(self.parentWidget().width() * self.progress_bar_size["width_percent"])
        self.progress_bar_rect.setHeight(self.parentWidget().height() * self.progress_bar_size["height_percent"])
        self.setGeometry(self.progress_bar_rect)

    def load_segments_from_json(self, file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
            segments_data = data.get("segments", [])
            CustomProgressBar.total_duration = sum(segment["length"] for segment in segments_data)
            current_x = 0
            for segment in segments_data:
                self.segments.append(Segment(segment["length"], segment["color"],
                                             self.progress_bar_size,
                                             current_x, self))
                current_x += segment["length"] / CustomProgressBar.total_duration * self.progress_bar_rect.width()
                self.segments[-1].setGeometry(self.progress_bar_rect)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(QPen(Qt.NoPen))
        painter.setBrush(Qt.lightGray)
        painter.drawRect(self.progress_bar_rect)

    def start_timer(self):
        CustomProgressBar.elapsed_time = 0
        CustomProgressBar.total_elapsed_time = 0
        CustomProgressBar.current_segment = 0
        self.timer.start(self.timer_interval)

    def timer_event(self):
        CustomProgressBar.elapsed_time += self.timer_interval
        CustomProgressBar.total_elapsed_time += self.timer_interval
        segment_duration = self.segments[CustomProgressBar.current_segment].length * 1000
        if CustomProgressBar.elapsed_time >= segment_duration:
            CustomProgressBar.elapsed_time = 0
            CustomProgressBar.current_segment = (CustomProgressBar.current_segment + 1) % len(self.segments)
        
        if CustomProgressBar.total_elapsed_time >= CustomProgressBar.total_duration * 1000:
            self.timer.stop()
        self.moving_hand.update()


    def createMovingHand(self):
        self.moving_hand = MovingHand(self, self.progress_bar_size)
        self.moving_hand.setGeometry(self.progress_bar_rect)
        
class Segment(CustomProgressBar):

    def __init__(self, length, color, progress_bar_size, current_x, parent):
        super().__init__(parent.parentWidget(), progress_bar_size)
        self.length = length 
        self.color = color
        self.progress_bar_size = progress_bar_size
        self.current_x = current_x
        self.offset = QPoint(0, 0)
        self.segment_width = (self.length / CustomProgressBar.total_duration) * self.progress_bar_rect.width()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            print("click")
            self.dragging = True
            #self.offset = event.pos()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(QPen(Qt.NoPen))
        painter.setBrush(QColor(self.color))
        painter.drawRect(self.current_x, self.progress_bar_rect.height() / 4,
                        self.segment_width, self.progress_bar_rect.height() / 2)

class MovingHand(CustomProgressBar):
    def __init__(self, parent, progress_bar_size):
        super().__init__(parent.parentWidget(), progress_bar_size)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        moving_hand_x = CustomProgressBar.total_elapsed_time / 1000 / CustomProgressBar.total_duration * self.progress_bar_rect.width()
        painter.setPen(QPen(Qt.black, 3))
        painter.drawLine(moving_hand_x, 0, moving_hand_x, self.progress_bar_rect.y() + self.progress_bar_rect.height())

def load_config(file_path):
    with open(file_path, 'r') as f:
        config_data = json.load(f)
    return config_data

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = QWidget()
    main_window.setWindowTitle("Custom Progress Bar")
    main_window.setGeometry(100, 100, 400, 200)

    layout = QVBoxLayout(main_window)

    config_data = load_config('config.json')
    progress_bar = CustomProgressBar(config_data['progress_bar'])  # Set the main_window as the parent
    progress_bar.load_segments_from_json("workout.json")
    progress_bar.start_timer()

    layout.addWidget(progress_bar)

    main_window.show()
    progress_bar.show()

    sys.exit(app.exec_())