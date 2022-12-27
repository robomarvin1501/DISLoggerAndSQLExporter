import sys

import matplotlib
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt5 import QtCore, QtWidgets

matplotlib.use("Qt5Agg")


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

    def _calculate_clicked_x_position(self, e):
        parent = self.parent()
        hmin, hmax = None, None

    def mousePressEvent(self, event):
        print(f"xmax: {self.size().width()}, xcurrent: {event.pos().x()}")
        # event.pos().x()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Create teh matplotlib figureCanvas
        # which defines a single set of axes as self.axes
        sc = MplCanvas(self, width=5, height=4, dpi=100)
        sc.axes.plot([0, 1, 2, 3, 4], [10, 1, 20, 3, 40])
        self.setCentralWidget(sc)

        self.show()



from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt


class _Timeline(QtWidgets.QWidget):
    # clickedValue = QtCore.pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super(_Timeline, self).__init__(*args, **kwargs)

        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )


    def _trigger_refresh(self):
        self.update()

    def _calculate_clicked_position(self, e):
        parent = self.parent()
        click_x_position = e.x()
        print(click_x_position)

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        self._calculate_clicked_position(a0)

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self._calculate_clicked_position(a0)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        sc = MplCanvas(self, width=5, height=4, dpi=100)
        sc.axes.plot([0, 1, 2, 3, 4], [10, 1, 20, 3, 40])


class TimeLineGreater(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(TimeLineGreater, self).__init__(*args, **kwargs)

        layout = QtWidgets.QVBoxLayout()
        self._timeline = _Timeline()
        layout.addWidget(self._timeline)

        self.label = QtWidgets.QLabel()
        self.label.setText("Hello world")
        layout.addWidget(self.label)

        self.setLayout(layout)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    tlg = TimeLineGreater()
    tlg.show()
    app.exec_()
