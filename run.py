import os
import importlib
from pathlib import Path
import time
import argparse
from helpers.glob_match import glob_match

PIPELINES = [
    "selection",
    "web",
    "keywords",
    "score",
    "commitment",
    "links",
    "socials",
    "address",
    "name",
    "logo",
    "about",
]

program = argparse.ArgumentParser(description="Run a pipeline")

program.add_argument(
    "pipelines",
    nargs="*",
    default=PIPELINES,
    help="the pipeline(s) to run",
)

# TODO: Add support for domain, url, and reset options
# program.add_argument(
#     "--domain",
#     help="the domain(s) to scrape (you can use GLOB wildcards, like * and ?)",
# )
#
# program.add_argument(
#     "--url",
#     help="the URL(s) to scrape (you can use GLOB wildcards, like * and ?)",
# )
#
# program.add_argument(
#     "--reset",
#     action="store_true",
#     help="restart the scraping from the beginning (do not continue from the last URL analyzed)",
# )

args = program.parse_args()

# Find pipelines to run, based on the user provided glob
pipelines_to_run = args.pipelines

for pipeline in pipelines_to_run:
    print("Running pipeline", pipeline, "...")

    # Load the pipeline
    module = importlib.import_module("." + pipeline, "pipelines")
    run_pipeline = getattr(module, "run_pipeline")

    # Run the pipeline
    start = time.perf_counter()
    run_pipeline(domain=None, url=None, reset=False)

    print(
        "Running pipeline",
        pipeline,
        "...",
        "Done!",
        "(%.2fs)" % (time.perf_counter() - start),
    )
