import queue
import sys

from logger_jumping import PlaybackLoggerFile
import DataExporterUi
from timeline import _Timeline

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QListWidgetItem, QFileDialog, QLabel
from PyQt5.QtCore import QThread

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
        self.position_mapper = interp1d([0, 100], [0, self.length_logger_file])
        self.timeline_width = 100

        self.play_back_loggerfile: PlaybackLoggerFile = None
        self._data_channel = queue.SimpleQueue()

        self._display_time(0)

    def _loading_finished(self):
        self.play_back_loggerfile: PlaybackLoggerFile = self._data_channel.get()
        del self.loader
        self.make_timeline()
        self.length_logger_file = self.play_back_loggerfile.playback_manager.logger_pdus[-1][1]
        self._display_time(0)

        self._connect_ui()

    def _connect_ui(self):
        self.buttonPlay.clicked.connect(self._play)
        self.buttonStop.clicked.connect(self._stop)
        self.buttonPause.clicked.connect(self._pause)

    def _play(self):
        self.buttonPlay.setDisabled(True)
        self.buttonStop.setDisabled(False)
        self.buttonPause.setDisabled(False)

    def _stop(self):
        self.buttonPlay.setDisabled(False)
        self.buttonStop.setDisabled(True)
        self.buttonPause.setDisabled(True)

    def _pause(self):
        self.buttonPlay.setDisabled(False)
        self.buttonStop.setDisabled(False)
        self.buttonPause.setDisabled(True)

    def make_timeline(self):
        self.TimeLine = _Timeline()
        self.TimeLine.selected_mouse_position.connect(self._updated_position)
        self.TimeLine.max_size.connect(self._changed_size)
        self.TimeLine.current_mouse_position.connect(self._moved_mouse)
        self.verticalLayout.addWidget(self.TimeLine)

    def _choose_file(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        # dlg.setFilter("LZMA files (*.lzma)")
        # TODO get the length of the logger from the logger, connect frontend to backend

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

    def _updated_position(self, x_pos: int):
        if x_pos < 0:
            x_pos = 0
        elif x_pos > self.timeline_width:
            x_pos = self.timeline_width
        logger_position = self.position_mapper(x_pos)
        self._display_time(logger_position)

    def _moved_mouse(self, x_pos: int):
        if x_pos < 0:
            x_pos = 0
        elif x_pos > self.timeline_width:
            x_pos = self.timeline_width
        logger_position = self.position_mapper(x_pos)
        self._display_time(logger_position)

    def _changed_size(self, width: int):
        self.timeline_width = width
        self.position_mapper = interp1d([0, width], [0, self.length_logger_file])


def main():
    app = QApplication(sys.argv)
    form = DataExporterTester()
    form.show()
    app.exec_()


if __name__ == "__main__":
    main()
