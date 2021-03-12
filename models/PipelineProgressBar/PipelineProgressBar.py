from .ProgressBar import ProgressBar
from .Controller import Controller
import shutil
import math
import sys


def move_to_previous_line():
    sys.stdout.write("\033[A")


def clear_current_line():
    sys.stdout.write("\r\033[K")


# A simple wrapper around progressbar2's ProgressBar
class PipelineProgressBar:
    def __init__(self, name, max_value=None, handler=None, current=0):
        self.status = None
        self._max_value = max_value
        self.bar = ProgressBar(
            current=current,
            max_value=max_value,
            prefix=f"{name.upper()} ",
            redirect_stdout=False,
        )
        self.current = current
        self.handler = handler or Controller()
        self.handler.add_bar(self)

    def add_bar(self, *args, **kwargs):
        kwargs["handler"] = self.handler
        return self.__class__(*args, **kwargs)

    @property
    def max_value(self):
        return self._max_value

    @max_value.setter
    def max_value(self, value):
        self.bar.max_value = value
        self._max_value = value
        self.update_bar()

    # Start the progressbar
    def iterate(self, array):
        self.max_value = len(array)
        while self.current < self.max_value:
            yield array[self.current]
            self.item_complete()
        self.finish()

    def set_status(self, status):
        self.handler.clear()
        self.status = status
        self.handler.render()

    # DEPRECATED
    def set_current_url(self, url):
        self.set_status(f"Analyzing: {url}")

    # Print a note
    def print(self, *args):
        self.handler.print(*args)

    def _print_status(self):
        if self.status is None:
            return

        sys.stdout.write(self.status)
        sys.stdout.write("\n")

    def _clear(self):
        clear_current_line()
        self._clear_status()

    # Clear the current status from the screen
    def _clear_status(self):
        if self.status is None:
            return

        last_url_length = len(self.status)
        terminal_width = shutil.get_terminal_size().columns
        lines_occupied = math.ceil(last_url_length / terminal_width)
        for _ in range(lines_occupied):
            move_to_previous_line()
            clear_current_line()

    def update_bar(self):
        self.handler.update_bars()

    # Mark item as complete and move progress forward
    def item_complete(self):
        self.current += 1
        self.update_bar()

    # Finish the progress bar
    def finish(self):
        self.handler.finish_bar(self)
