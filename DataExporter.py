import datetime
import queue
import sys
import time

from logger_jumping import PlaybackLoggerFile
import DataExporterUi
from timeline import _Timeline

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QApplication, QListWidgetItem, QFileDialog, QLabel, QShortcut
from PyQt5.QtCore import QThread, QTimer

from scipy.interpolate import interp1d


class FileLoader(QThread):
    def __init__(self, filepath: str, data_pipe_sender: queue.SimpleQueue):
        super().__init__()
        self._filepath = filepath
        self._exercise_id = 97  # TODO set dynamically
        self._data_pipe = data_pipe_sender

    def run(self):
        plg = PlaybackLoggerFile(self._filepath, self._exercise_id)
        self._data_pipe.put(plg)


class DataExporterTester(QtWidgets.QMainWindow, DataExporterUi.Ui_MainWindow):
    def __init__(self, parent=None):
        super(DataExporterTester, self).__init__(parent)
        self.setupUi(self)

        self.logger_file_name = ""
        self.actionOpenFile.triggered.connect(self._choose_file)

        self.length_logger_file = 0
        # maps the timeline position to the time in the logger file
        self.position_mapper = interp1d([0, 100], [0, self.length_logger_file])
        self.time_mapper = interp1d([0, self.length_logger_file], [0, 100])
        self.timeline_width = 100

        self.play_back_loggerfile: PlaybackLoggerFile = None
        self._data_channel = queue.SimpleQueue()

        self._starting_worldtime = 0
        self._starting_packettime = 0
        self._approximate_current_packettime = 0
        self._change_playback_position_timer = QTimer()
        self._change_playback_position_timer.timeout.connect(self._timer_timeout)

        self._display_time(0)
        self._setup_shortcuts()

        self.playback_speed = 1

        self.buttonPlay.setDisabled(True)
        self.buttonStop.setDisabled(True)
        self.buttonPause.setDisabled(True)
        self.buttonIncreaseSpeed.setDisabled(True)
        self.buttonDecreaseSpeed.setDisabled(True)

    def _loading_finished(self):
        self.play_back_loggerfile: PlaybackLoggerFile = self._data_channel.get()
        del self.loader
        self.make_timeline()
        self.length_logger_file = self.play_back_loggerfile.playback_manager.logger_pdus[-1][1]
        self._display_time(0)

        self._connect_ui()

        self.buttonPlay.setDisabled(False)
        self.buttonStop.setDisabled(True)
        self.buttonPause.setDisabled(True)
        self.buttonIncreaseSpeed.setDisabled(False)

    def _timer_timeout(self):
        if self._approximate_current_packettime >= self.play_back_loggerfile.playback_manager._maximum_time - 0.5:
            self._stop()
        self._approximate_current_packettime += self._change_playback_position_timer.interval() * self.playback_speed / 1000

        timeline_position = self.time_mapper(self._approximate_current_packettime)
        self.TimeLine._calculate_mouse(timeline_position)
        self.TimeLine._trigger_refresh()

        self.change_position_by_time(self._approximate_current_packettime)

    def _connect_ui(self):
        self.buttonPlay.clicked.connect(self._play)
        self.buttonStop.clicked.connect(self._stop)
        self.buttonPause.clicked.connect(self._pause)

        self.buttonIncreaseSpeed.clicked.connect(self._increase_speed)
        self.buttonDecreaseSpeed.clicked.connect(self._decrease_speed)

    def _setup_shortcuts(self):
        self.shortcut_open = QShortcut(QKeySequence("Ctrl+O"), self)
        self.shortcut_open.activated.connect(self._choose_file)

    def _play(self):
        self.buttonPlay.setDisabled(True)
        self.buttonStop.setDisabled(False)
        self.buttonPause.setDisabled(False)

        self.play_back_loggerfile.play()
        self._change_playback_position_timer.start(10)

    def _stop(self):
        stopped_playback = datetime.datetime.now().timestamp()
        self.buttonPlay.setDisabled(False)
        self.buttonStop.setDisabled(True)
        self.buttonPause.setDisabled(True)

        time.sleep(0.3)
        self.play_back_loggerfile.stop()
        self._set_timeline_position(stopped_playback)

        self._change_playback_position_timer.stop()

    def _pause(self):
        stopped_playback = datetime.datetime.now().timestamp()
        self.buttonPlay.setDisabled(False)
        self.buttonStop.setDisabled(True)
        self.buttonPause.setDisabled(True)

        self.play_back_loggerfile.pause()
        self._set_timeline_position(stopped_playback)

        self._change_playback_position_timer.stop()

    def _increase_speed(self):
        if self.playback_speed == 5:
            self.buttonIncreaseSpeed.setDisabled(True)
            return
        elif self.playback_speed == 4:
            self.buttonIncreaseSpeed.setDisabled(True)
        self.buttonDecreaseSpeed.setDisabled(False)
        self.playback_speed += 1
        self.play_back_loggerfile.set_playback_speed(self.playback_speed)
        self.labelPlaybackSpeed.setText(str(self.playback_speed) + ".0x")
        self.update()

    def _decrease_speed(self):
        if self.playback_speed == 1:
            self.buttonDecreaseSpeed.setDisabled(True)
            return
        elif self.playback_speed == 2:
            self.buttonDecreaseSpeed.setDisabled(True)
        self.buttonIncreaseSpeed.setDisabled(False)
        self.playback_speed -= 1
        self.play_back_loggerfile.set_playback_speed(self.playback_speed)
        self.labelPlaybackSpeed.setText(str(self.playback_speed) + ".0x")
        self.update()

    def _set_timeline_position(self, stopped_playback_time: float):
        while stopped_playback_time > self.play_back_loggerfile.playback_manager.stop_time:
            time.sleep(0.1)
        # TODO need a better way of getting the current time
        current_time = self.play_back_loggerfile.playback_manager.logger_pdus[
            self.play_back_loggerfile.playback_manager.position_pointer][1]
        print(current_time)
        self.change_position_by_time(current_time)
        self.TimeLine._trigger_refresh()

    def make_timeline(self):
        self.TimeLine = _Timeline()
        self.TimeLine.selected_mouse_position.connect(self._updated_position)
        self.TimeLine.max_size.connect(self._changed_size)
        self.TimeLine.current_mouse_position.connect(self._moved_mouse)
        self.verticalLayout.addWidget(self.TimeLine)

    def _choose_file(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)

        if dlg.exec_():
            filenames = dlg.selectedFiles()
            if len(filenames) < 1:
                print("No file selected")
                return ""
            elif len(filenames) > 1:
                print("You selected more than one file, the first will be loaded")
            self.logger_file_name = filenames[0]
            self.preciseTime.setText(f"Loading: {filenames[0]}")

            self.loader = FileLoader(self.logger_file_name, self._data_channel)
            self.loader.finished.connect(self._loading_finished)
            self.loader.start()

    def _display_time(self, position: float):
        self.preciseTime.setText(f"Current: {position:.2f}s | Length: {self.length_logger_file:.2f}s")

    def change_position_by_time(self, time: float):
        timeline_position = self.time_mapper(time)
        self.TimeLine._calculate_mouse(timeline_position)
        # Not using updated position because this also moves the play_back_loggerfile
        # TODO combine updated_position and moved_mouse into one function with a boolean flag for movng the logger
        self._moved_mouse(timeline_position)

    def _updated_position(self, x_pos: int):
        if x_pos < 0:
            x_pos = 0
        elif x_pos > self.timeline_width:
            x_pos = self.timeline_width
        logger_position = self.position_mapper(x_pos)
        self._approximate_current_packettime = logger_position
        self._display_time(logger_position)
        self.play_back_loggerfile.playback_manager.remove_all_entities()
        self.play_back_loggerfile.move(logger_position)

    def _moved_mouse(self, x_pos: int):
        if x_pos < 0:
            x_pos = 0
        elif x_pos > self.timeline_width:
            x_pos = self.timeline_width
        logger_position = self.position_mapper(x_pos)
        self._approximate_current_packettime = logger_position
        self._display_time(logger_position)

    def _changed_size(self, width: int):
        self.timeline_width = width
        self.position_mapper = interp1d([0, width], [0, self.length_logger_file])
        self.time_mapper = interp1d([0, self.length_logger_file], [0, width])


def main():
    app = QApplication(sys.argv)
    form = DataExporterTester()
    form.show()
    app.exec_()


if __name__ == "__main__":
    main()
