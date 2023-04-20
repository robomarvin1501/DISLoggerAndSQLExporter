import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt


def clamp(x: float, minimum: float, maximum: float) -> float:
    """
    Limits a number to between the maximum and minimum values
    :param x: float
    :param minimum: float
    :param maximum: float
    :return: float
    """
    return max(min(maximum, x), minimum)


class _Timeline(QtWidgets.QWidget):
    """
    A class which produces a widget that bears similarities to a timeline. It transmits no information to the user other
    than a visual representation of how far along they are, but that's the way the cat vomits.
    """
    selected_mouse_position = QtCore.pyqtSignal(int)
    current_mouse_position = QtCore.pyqtSignal(int)
    max_size = QtCore.pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        """
        :param args:   : Left empty in the instantiation in DataExporter.py, for I have nothing to add
        :param kwargs: : Left empty in the instantiation in DataExporter.py, for I have nothing to add
        """
        super(_Timeline, self).__init__(*args, **kwargs)

        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

        self._background_colour = QtGui.QColor("black")
        self._padding = 4.0

        self.current_mouse_position_ratio = 0
        self.maximum_bar_value = 1

    def _trigger_refresh(self) -> None:
        """
        I... I don't need to document this, right? Like seriously, it shouldn't be necessary. The name should make it
        obvious that it updates the way that the widget looks.
        I suppose I could write a justification for its existence, it provides future proofing for potential necessities
        that need to be run on every update, a safer way of connecting to an inherited method, and was in the tutorial
        that I read to learn about custom widgets, so I decided to leave it in, but I don't think anyone is interested
        in all that.
        :return: None
        """
        self.update()

    def _calculate_mouse(self, x: int) -> None:
        """
        Calculates, and sets, the x position as a fraction of the width of the timeline.
        :param x: int
        :return: None
        """
        self.current_mouse_position_ratio = x / self.maximum_bar_value

    def _calculate_clicked_position(self, e):
        parent = self.parent()
        click_x_position = e.x()
        self._calculate_mouse(click_x_position)
        self.selected_mouse_position.emit(int(click_x_position))

    def _calculate_moved_position(self, e: PyQt5.QtGui.QMouseEvent) -> None:
        """
        Calculates the x position when the mouse is dragged, and sets the bar to that position.
        :param e: PyQt5.QtGui.QMouseEvent
        :return: None
        """
        parent = self.parent()
        moved_x_position = e.x()
        self._calculate_mouse(moved_x_position)
        self.current_mouse_position.emit(int(moved_x_position))

        self._trigger_refresh()

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        """
        Is called every time the mouse is dragged. Calls a method to calculate the new x position, and display it.
        :param a0: QtGui.QMouseEvent
        :return: None
        """
        self._calculate_moved_position(a0)

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        """
        When the mouse is clicked on a position, ie the left button is released, this method is called, and recalculates
        the locations
        :param a0:
        :return:
        """
        self._calculate_clicked_position(a0)

        self._trigger_refresh()

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        """
        Overrides the method of the base class with what I want to happen, mwahahaha! You cannot stop me!
        Ahem.
        Paints the incredibly simple timeline. What goes into it?
            - A black background
            - A little padding to make it prettier, and not go right to the edge of the background
            - Actually drawing the bar. It is blue, solid, and big.
        :param a0: QtGui.QPaintEvent
        :return: None
        """
        # region background
        painter = QtGui.QPainter(self)
        brush = QtGui.QBrush()
        brush.setColor(self._background_colour)
        brush.setStyle(Qt.SolidPattern)
        rect = QtCore.QRect(0, 0, painter.device().width(), painter.device().height())
        self.max_size.emit(painter.device().width())
        painter.fillRect(rect, brush)
        # endregion

        self.maximum_bar_value = painter.device().width()

        # region bar_position
        # Define canvas
        d_height = painter.device().height() - (self._padding * 2)
        d_width = painter.device().width() - (self._padding * 2)

        actual_x_position = clamp(self.current_mouse_position_ratio * self.maximum_bar_value, 0, d_width)

        # Draw bar
        brush.setColor(QtGui.QColor("blue"))
        rect = QtCore.QRect(
            int(self._padding),
            int(self._padding),
            int(actual_x_position),
            int(d_height)
        )
        painter.fillRect(rect, brush)

        # endregion
        painter.end()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    tlg = _Timeline()
    tlg.show()
    app.exec_()
