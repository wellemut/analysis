from contextlib import contextmanager
import os
import sys

# Suppress python print output, useful for noisy 3rd party libraries
# See: https://stackoverflow.com/questions/4178614/suppressing-output-of-module-calling-outside-library
@contextmanager
def suppress_stdout_and_stderr():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = devnull
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
