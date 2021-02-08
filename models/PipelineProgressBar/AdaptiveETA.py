import progressbar

# Custom AdaptiveETA widget that correctly displays finished when max_value is 0
class AdaptiveETA(progressbar.AdaptiveETA):
    def __call__(self, progress, data):
        if data["max_value"] == 0:
            return progressbar.Timer.__call__(
                self, progress, data, format=self.format_finished
            )
        else:
            return super(AdaptiveETA, self).__call__(progress, data)
