from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt


def clamp(x: float, minimum: float, maximum: float):
    return max(min(maximum, x), minimum)


class _Timeline(QtWidgets.QWidget):
    selected_mouse_position = QtCore.pyqtSignal(int)
    current_mouse_position = QtCore.pyqtSignal(int)
    max_size = QtCore.pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super(_Timeline, self).__init__(*args, **kwargs)

        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

        self._background_colour = QtGui.QColor("black")
        self._padding = 4.0

        self.current_mouse_position_value = 0

    def _trigger_refresh(self):
        self.update()

    def _calculate_clicked_position(self, e):
        parent = self.parent()
        click_x_position = e.x()
        self.current_mouse_position_value = click_x_position
        self.selected_mouse_position.emit(int(click_x_position))

    def _calculate_moved_position(self, e):
        parent = self.parent()
        moved_x_position = e.x()
        self.current_mouse_position_value = moved_x_position
        self.current_mouse_position.emit(int(moved_x_position))

        self._trigger_refresh()

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        self._calculate_moved_position(a0)

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        self._calculate_clicked_position(a0)

        self._trigger_refresh()

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        # region background
        painter = QtGui.QPainter(self)
        brush = QtGui.QBrush()
        brush.setColor(self._background_colour)
        brush.setStyle(Qt.SolidPattern)
        rect = QtCore.QRect(0, 0, painter.device().width(), painter.device().height())
        self.max_size.emit(painter.device().width())
        painter.fillRect(rect, brush)
        # endregion

        # region bar_position
        # Define canvas
        d_height = painter.device().height() - (self._padding * 2)
        d_width = painter.device().width() - (self._padding * 2)

        # Draw bar
        brush.setColor(QtGui.QColor("blue"))
        rect = QtCore.QRect(
            int(self._padding),
            int(self._padding),
            int(clamp(self.current_mouse_position_value, 0, d_width)),
            int(d_height)
        )
        painter.fillRect(rect, brush)

        # endregion
        painter.end()


class TimeLineGreater(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(TimeLineGreater, self).__init__(*args, **kwargs)

        layout = QtWidgets.QVBoxLayout()
        self._timeline = _Timeline()
        self._timeline.clickedValue.connect(self._updated_position)
        layout.addWidget(self._timeline)

        self.label = QtWidgets.QLabel()
        self.label.setText("Hello world")
        layout.addWidget(self.label)

        self.setLayout(layout)

    def _updated_position(self, x_pos: int):
        print(f"From DET: {x_pos}")


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    tlg = TimeLineGreater()
    tlg.show()
    app.exec_()
