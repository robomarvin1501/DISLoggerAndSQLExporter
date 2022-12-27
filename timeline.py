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

        self._background_colour = QtGui.QColor("black")
        self._padding = 4.0

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
        painter = QtGui.QPainter(self)
        brush = QtGui.QBrush()
        brush.setColor(self._background_colour)
        brush.setStyle(Qt.SolidPattern)
        rect = QtCore.QRect(0, 0, painter.device().width(), painter.device().height())
        painter.fillRect(rect, brush)


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
