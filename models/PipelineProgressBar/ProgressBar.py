import progressbar
from .Percentage import Percentage
from .SimpleProgress import SimpleProgress
from .Bar import Bar
from .AdaptiveETA import AdaptiveETA


class ProgressBar(progressbar.ProgressBar):
    # Use the standard widgets, even when max_value is zero
    def default_widgets(self):
        return [
            Percentage(**self.widget_kwargs),
            " ",
            SimpleProgress(
                format="(%s)" % SimpleProgress.DEFAULT_FORMAT, **self.widget_kwargs
            ),
            " ",
            Bar(**self.widget_kwargs),
            " ",
            progressbar.Timer(**self.widget_kwargs),
            " ",
            AdaptiveETA(**self.widget_kwargs),
        ]
