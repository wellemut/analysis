from progressbar import ProgressBar
import shutil
import math
import sys

# A simple wrapper around progressbar2's ProgressBar
class PipelineProgressBar:
    def __init__(self, pipeline_name):
        self.pipeline_name = pipeline_name
        self.max_value = None
        self.status = None
        self.bar = None
        self.current = 0

    # Start the progressbar
    def iterate(self, array):
        self.max_value = len(array)
        self.init_bar()
        self.start()
        while self.current < self.max_value:
            yield array[self.current]
            self.item_complete()

        # Clear the current line (progressbar)
        self.clear_current_line()
        self.clear_status()
        self.finish()

    # Initialize the progressbar2 object
    def init_bar(self):
        self.bar = ProgressBar(
            max_value=self.max_value,
            prefix=f"{self.pipeline_name.upper()} ",
            redirect_stdout=True,
        )

    def set_current_url(self, url):
        # Clear previous URL
        self.clear_status()

        # Print new URL
        self.status = f"Analyzing: {url}"
        self.print_status()

    # Print a note above the current URL being analyzed
    def print(self, *args):
        self.clear_status()
        print(*args)
        self.print_status()

    # Clear the current status from the screen
    def clear_status(self):
        if not self.status:
            return

        last_url_length = len(self.status)
        terminal_width = shutil.get_terminal_size().columns
        lines_occupied = math.ceil(last_url_length / terminal_width)
        for _ in range(lines_occupied):
            self.move_to_previous_line()
            self.clear_current_line()

    def print_status(self):
        if not self.status:
            return

        print(self.status)
        self.update_bar()

    def move_to_previous_line(self):
        sys.stdout.write("\033[A")

    def clear_current_line(self):
        sys.stdout.write("\r\033[K")

    # Start the progress bar
    def start(self):
        self.bar.start()

    # Finish the progress bar
    def finish(self):
        self.bar.finish()

    def update_bar(self):
        self.bar.update(self.current, force=True)

    # Mark item as complete and move progress forward
    def item_complete(self):
        self.current += 1
        self.update_bar()
