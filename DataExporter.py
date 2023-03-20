import threading
import lzma
import json
import sys

from logger import DISReceiver, DataWriter
import DataExporterUi
from timeline import _Timeline

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QListWidgetItem

from scipy.interpolate import interp1d


class DataExporterElectricBoogaloo(QtWidgets.QMainWindow, DataExporterUi.Ui_MainWindow):
    def __init__(self, parent=None):
        super(DataExporterElectricBoogaloo, self).__init__(parent)
        self.setupUi(self)

        self.record_toggle_setup()
        self.data_logger = threading.Thread(target=self.logger_thread, daemon=True)
        self.current = 0

    def record_toggle_setup(self):
        self.record_toggle.clicked.connect(self.toggle_recording)

    def print(self, s: str):
        s_text = QListWidgetItem(s)
        self.stdout_listwidget.addItem(s_text)

    def toggle_recording(self):
        if self.record_toggle.isChecked():
            print("Recording")
            self.print("Recording")
            self.data_logger.start()
        else:
            print("Not recording")
            self.print("Not recording")
            self.data_logger = threading.Thread(target=self.logger_thread, daemon=True)

    def logger_thread(self):
        try:
            with open("DataExporterConfig.json", 'r') as f:
                config_data = json.load(f)
        except FileNotFoundError:
            self.print(r"""
                ERROR: No configuration file
                Please write a configuration file in the base folder by the name "DataExporterConfig.json"
                For examples, see \\files\docs\DataExporter\DataExporterConfig.json
            """)
            sys.exit()

        if config_data["logger_file"][-5:] != ".lzma":
            config_data["logger_file"] += ".lzma"

        lzc = lzma.LZMACompressor()

        EXERCISE_ID = config_data["exercise_id"]
        export = config_data["export_to_sql"]
        logger_file = config_data["logger_file"]
        db_name = config_data["database_name"]
        new_db = config_data["new_database"]
        with DataWriter(logger_file, "logs", lzc, output_writer=self.print) as writer:
            with DISReceiver(3000, EXERCISE_ID, msg_len=16_384, output_writer=self.print) as r:
                for (address, data, packettime, world_timestamp) in r:
                    # NOTE floats are doubles in C, so use struct.unpack('d', packettime) on them
                    # self.print(str(data))
                    self.current += 1
                    if self.current % 100 == 0:
                        self.message_count.setText(str(self.current))
                    writer.write(data, packettime, world_timestamp)
                    if not self.record_toggle.isChecked():
                        break


class DataExporterTester(QtWidgets.QMainWindow, DataExporterUi.Ui_MainWindow):
    def __init__(self, parent=None):
        super(DataExporterTester, self).__init__(parent)
        self.setupUi(self)
        self.make_timeline()

        self.length_logger_file = 2000
        self.position_mapper = interp1d([0, 100], [0, self.length_logger_file])
        self.timeline_width = 100

        self._display_time(0)

    def make_timeline(self):
        self.TimeLine = _Timeline()
        self.TimeLine.selected_mouse_position.connect(self._updated_position)
        self.TimeLine.max_size.connect(self._changed_size)
        self.TimeLine.current_mouse_position.connect(self._moved_mouse)
        self.verticalLayout.addWidget(self.TimeLine)

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
