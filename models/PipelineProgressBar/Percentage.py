import progressbar

# Custom Percentage widget, that displays 0% instead of N/A when percentage is 0
class Percentage(progressbar.Percentage):
    def __call__(self, progress, data, *args, **kwargs):
        # If percentage is not available, display N/A%
        if "percentage" in data and data["percentage"] is None:
            return progressbar.widgets.FormatWidgetMixin.__call__(
                self, progress, data, format="N/A%%"
            )

        return progressbar.widgets.FormatWidgetMixin.__call__(self, progress, data)
