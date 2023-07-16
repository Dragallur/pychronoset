import sys
import json
import time
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout

class CustomProgressBar(QWidget):
    def __init__(self, progress_bar_size, parent=None):
        super().__init__(parent)
        self.segments = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timer_event)
        self.timer_interval = 100  # milliseconds
        self.current_segment = 0
        self.elapsed_time = 0
        self.total_elapsed_time = 0
        self.total_duration = 0
        self.progress_bar_size = progress_bar_size

    def load_segments_from_json(self, file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
            self.segments = data.get("segments", [])
            self.total_duration = sum(segment["length"] for segment in self.segments)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the progress bar background
        progress_bar_rect = self.rect()
        progress_bar_rect.setX(self.parentWidget().width() * self.progress_bar_size["x_percent"])
        progress_bar_rect.setY(self.parentWidget().height() * self.progress_bar_size["y_percent"])
        progress_bar_rect.setWidth(self.parentWidget().width() * self.progress_bar_size["width_percent"])
        progress_bar_rect.setHeight(self.parentWidget().height() * self.progress_bar_size["height_percent"])
        painter.setPen(QPen(Qt.NoPen))
        painter.setBrush(Qt.lightGray)
        painter.drawRect(progress_bar_rect)

        current_x = progress_bar_rect.x()
        for segment in self.segments:
            segment_duration = segment["length"]
            segment_width = (segment_duration / self.total_duration) * progress_bar_rect.width()

            # Draw the segment
            color = QColor(segment["color"])
            painter.setPen(QPen(Qt.NoPen))
            painter.setBrush(color)
            painter.drawRect(current_x, progress_bar_rect.y() + progress_bar_rect.height() / 4,
                             segment_width, progress_bar_rect.height() / 2)

            current_x += segment_width

        # Draw the moving hand
        moving_hand_x = progress_bar_rect.x() + self.total_elapsed_time / 1000 / self.total_duration * progress_bar_rect.width()
        painter.setPen(QPen(Qt.black, 3))
        painter.drawLine(moving_hand_x, progress_bar_rect.y(), moving_hand_x, progress_bar_rect.y() + progress_bar_rect.height())

    def start_timer(self):
        self.elapsed_time = 0
        self.total_elapsed_time = 0
        self.current_segment = 0
        self.timer.start(self.timer_interval)

    def timer_event(self):
        self.elapsed_time += self.timer_interval
        self.total_elapsed_time += self.timer_interval
        segment_duration = self.segments[self.current_segment]["length"] * 1000
        if self.elapsed_time >= segment_duration:
            self.elapsed_time = 0
            self.current_segment = (self.current_segment + 1) % len(self.segments)
        
        if self.total_elapsed_time >= self.total_duration * 1000:
            self.timer.stop()

        self.update()

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