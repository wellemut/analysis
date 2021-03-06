import sys


def move_to_previous_line():
    sys.stdout.write("\033[A")


# Controls the printing and updating of single and multi progress
# bars
class Controller:
    def __init__(self):
        self.bars = []

    def add_bar(self, bar):
        self.clear()
        self.bars.insert(0, bar)
        self.render()

    def print(self, *args):
        self.clear()
        print(*args)
        self.render()

    def clear(self):
        if len(self.bars) == 0:
            return

        for bar in self.bars:
            move_to_previous_line()
            bar._clear()

    def update_bars(self):
        self.clear()
        self.render()

    def render(self):
        for bar in self.bars:
            bar._print_status()
            bar.bar.update(bar.current, force=True)
            sys.stdout.write("\n")

    def finish_bar(self, bar):
        self.clear()

        bar.bar.finish()
        self.bars.remove(bar)

        self.render()
