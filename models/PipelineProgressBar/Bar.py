import progressbar

# Custom marker that shows 100% when max value is 0
def marker(progress, data, width):
    if (
        progress.max_value is not progressbar.base.UnknownLength
        and progress.max_value > 0
    ):
        length = int(progress.value / progress.max_value * width)
        return "#" * length
    elif progress.max_value == 0:
        return "#" * width
    else:
        return "#"


class Bar(progressbar.Bar):
    def __init__(self, *args, **kwargs):
        super().__init__(marker=marker, *args, **kwargs)
