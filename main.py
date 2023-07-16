from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QVBoxLayout, QWidget
import sys
import json
import workout_bar as WB

def load_config(file_path):
    with open(file_path, 'r') as f:
        config_data = json.load(f)
    return config_data

if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = QDesktopWidget().screenGeometry()
    screen_width, screen_height = screen.width(), screen.height()
    config_data = load_config('config.json')
    main_window_x = int(config_data['main_window']['x_percent'] * screen_width)
    main_window_y = int(config_data['main_window']['y_percent'] * screen_height)
    main_window_width = int(config_data['main_window']['width_percent'] * screen_width)
    main_window_height = int(config_data['main_window']['height_percent'] * screen_height)

    main_window = QWidget()
    main_window.setWindowTitle("PyChronoSet")
    main_window.setGeometry(main_window_x, main_window_y, main_window_width, main_window_height)

    layout = QVBoxLayout(main_window)

    progress_bar = WB.CustomProgressBar(config_data['progress_bar'])
    progress_bar.load_segments_from_json("workout.json")
    progress_bar.start_timer()

    layout.addWidget(progress_bar)

    main_window.show()
    progress_bar.show()
    sys.exit(app.exec_())