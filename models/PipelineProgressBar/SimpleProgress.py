import progressbar

# Custom SimpleProgress widget, that displays 0 of 0 instead of 0 of N/A when
# max_value is 0
class SimpleProgress(progressbar.SimpleProgress):
    DEFAULT_FORMAT = "%(value_s)s of %(max_value_custom)s"

    def __call__(self, progress, data, *args, **kwargs):
        # If max_value is not available, display N/A
        # Otherwise, display the number, even if zero
        if data.get("max_value") is not progressbar.base.UnknownLength:
            data["max_value_custom"] = data.get("max_value")
        else:
            data["max_value_custom"] = "N/A"

        return super(SimpleProgress, self).__call__(progress, data, *args, **kwargs)
