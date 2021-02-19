import os
import importlib
from pathlib import Path
import time
import argparse
from helpers.glob_match import glob_match

program = argparse.ArgumentParser(description="Run a scraper")

program.add_argument(
    "pipeline",
    help="the pipeline to run",
)

program.add_argument(
    "--domain",
    help="the domain(s) to scrape (you can use GLOB wildcards, like * and ?)",
)

program.add_argument(
    "--url",
    help="the URL(s) to scrape (you can use GLOB wildcards, like * and ?)",
)

program.add_argument(
    "--reset",
    action="store_true",
    help="restart the scraping from the beginning (do not continue from the last URL analyzed)",
)

args = program.parse_args()

pipeline = args.pipeline
print("Running scraper", pipeline, "...")

# Load the pipeline
module = importlib.import_module("." + pipeline, "scrapers")
run_pipeline = getattr(module, "run_pipeline")

# Run the pipeline
start = time.perf_counter()
run_pipeline(domain=args.domain, url=args.url, reset=args.reset)

print(
    "Running scraper",
    pipeline,
    "...",
    "Done!",
    "(%.2fs)" % (time.perf_counter() - start),
)
