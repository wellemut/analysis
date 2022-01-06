# Matches the given dict against the expected dict.
# Test passes if all keys of expected are in this dict and the values are
# identical.
# Example:
# assert {"a": 2} == matches_dict({"a": 2, "b": 5})
class matches_dict(dict):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def __eq__(self, expected):
        # Remove any keys not expected
        for key in list(self):
            if key not in expected:
                self.pop(key)

        return super().__eq__(expected)
