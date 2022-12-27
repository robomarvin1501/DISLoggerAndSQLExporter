import threading
import lzma
import json
import sys

from logger import DISReceiver, DataWriter
import DataExporterUi
from timeline import _Timeline

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QListWidgetItem


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

    def make_timeline(self):
        self.TimeLine = _Timeline()
        self.verticalLayout.addWidget(self.TimeLine)


def main():
    app = QApplication(sys.argv)
    form = DataExporterTester()
    form.show()
    app.exec_()


if __name__ == "__main__":
    main()
