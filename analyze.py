import os
import importlib
from pathlib import Path
import argparse
from helpers.glob_match import glob_match

program = argparse.ArgumentParser(description="Analyze the scraped websites.")

program.add_argument(
    "--pipeline",
    help="the pipeline(s) to run (you can use GLOB wildcards, like * and ?)",
)

program.add_argument(
    "--domain",
    help="the domain(s) to analyze (you can use GLOB wildcards, like * and ?)",
)

program.add_argument(
    "--url",
    help="the URL(s) to analyze (you can use GLOB wildcards, like * and ?)",
)

program.add_argument(
    "--reset",
    action="store_true",
    help="restart the analysis from the beginning (do not continue from the last URL analyzed)",
)

args = program.parse_args()


# Find all available pipelines
pipelines = [Path(file).stem for file in os.listdir("pipelines")]

# Find pipelines to run, based on the user provided glob
pipeline_glob = args.pipeline or "*"
pipelines_to_run = []
for pipeline in pipelines:
    if glob_match(pipeline_glob, pipeline):
        pipelines_to_run.append(pipeline)

# Run each pipeline
for pipeline in pipelines_to_run:
    print("Running pipeline", pipeline, "...")

    # Load the pipeline
    module = importlib.import_module("." + pipeline, "pipelines")
    run_pipeline = getattr(module, "run_pipeline")

    # Run the pipeline
    run_pipeline(domain=args.domain, url=args.url, reset=args.reset)

    print("Running pipeline", pipeline, "...", "Done! :)")


# pipeline = "sdgs"
#
# # Load the pipeline
# module = importlib.import_module("." + pipeline, "pipelines")
# run_pipeline = getattr(module, "run_pipeline")

# Run the pipeline
# run_pipeline(domain=args.domain, url=args.url, reset=False)
