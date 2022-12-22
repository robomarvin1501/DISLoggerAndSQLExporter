from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt


# Example of making a custom widget

class _Bar(QtWidgets.QWidget):
    clickedValue = QtCore.pyqtSignal(int)

    def __init__(self, steps, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

        if isinstance(steps, list):
            self.n_steps = len(steps)
            self.steps = steps

        elif isinstance(steps, int):
            self.n_steps = steps
            self.steps = ["red"] * steps

        else:
            raise TypeError("Steps must be an int or a list")

        self._bar_solid_percent = 0.8
        self._background_colour = QtGui.QColor("black")
        self._padding = 4.0

    def _trigger_refresh(self):
        self.update()

    def _caculate_clicked_value(self, e):
        parent = self.parent()
        vmin, vmax = parent._dial.minimum(), parent._dial.maximum()
        d_height = self.size().height() + (self._padding * 2)
        step_size = d_height / self.n_steps
        click_y = e.y() - self._padding - step_size / 2

        pc = (d_height - click_y) / d_height
        value = vmin + pc * (vmax - vmin)
        self.clickedValue.emit(int(value))

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        self._caculate_clicked_value(a0)

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self._caculate_clicked_value(a0)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        brush = QtGui.QBrush()
        brush.setColor(self._background_colour)
        brush.setStyle(Qt.SolidPattern)
        rect = QtCore.QRect(0, 0, painter.device().width(), painter.device().height())
        painter.fillRect(rect, brush)

        # Get current state
        dial = self.parent()._dial
        vmin, vmax = dial.minimum(), dial.maximum()
        value = dial.value()

        # Define our canvas
        d_height = painter.device().height() - (self._padding * 2)
        d_width = painter.device().width() - (self._padding * 2)

        # Draw the bars
        step_size = d_height / self.n_steps
        bar_height = step_size * self._bar_solid_percent
        bar_spacer = step_size * (1 - self._bar_solid_percent) / 2

        pc = (value - vmin) / (vmax - vmin)
        n_steps_to_draw = int(pc * self.n_steps)
        brush.setColor(QtGui.QColor("red"))
        for n in range(n_steps_to_draw):
            brush.setColor(QtGui.QColor(self.steps[n]))
            rect = QtCore.QRect(
                int(self._padding),
                int(self._padding + d_height - ((n + 1) * step_size) + bar_spacer),
                int(d_width),
                int(bar_height)
            )
            painter.fillRect(rect, brush)
        painter.end()


class PowerBar(QtWidgets.QWidget):
    def __init__(self, steps=5, *args, **kwargs):
        super(PowerBar, self).__init__(*args, **kwargs)

        layout = QtWidgets.QVBoxLayout()
        self._bar = _Bar(steps)
        layout.addWidget(self._bar)

        self._dial = QtWidgets.QDial()
        self._dial.valueChanged.connect(self._bar._trigger_refresh)
        layout.addWidget(self._dial)

        # Take feedback from click events
        self._bar.clickedValue.connect(self._dial.setValue)

        self.setLayout(layout)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    volume = PowerBar(10)
    volume.show()
    app.exec_()
