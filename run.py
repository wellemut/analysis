import argparse
import pipelines

pipeline_names = ", ".join(pipelines.names)
program = argparse.ArgumentParser(
    description=f"Run one or several domains through all pipelines ({pipeline_names})",
    epilog="Example: python ./run.py example.com test.com --only scrape extract",
)
program.add_argument(
    "domains", metavar="domain", nargs="+", help="one or more domains to analyze"
)
program.add_argument(
    "--only",
    metavar="pipeline",
    nargs="+",
    choices=pipelines.names,
    help=f"limit the analysis to the given pipelines ({pipeline_names})",
)
program.add_argument(
    "--skip",
    metavar="pipeline",
    nargs="+",
    choices=pipelines.names,
    help=f"skip the analysis for the given pipelines ({pipeline_names})",
)
args = program.parse_args()

# Determine pipelines to run
pipelines_to_run = pipelines.names
if args.only and args.skip:
    raise Exception("The options --only and --skip cannot be combined.")

if args.only:
    pipelines_to_run = args.only

if args.skip:
    pipelines_to_run = filter(lambda x: x not in args.skip, pipelines_to_run)

# Run each domain through the requested pipelines
for domain in args.domains:
    for pipeline in pipelines_to_run:
        pipelines.run(pipeline, domain)