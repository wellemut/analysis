import argparse
import pipelines

program = argparse.ArgumentParser(
    description="Run one or several domains through all pipelines",
    epilog="Example: python ./run.py example.com test.com",
)
program.add_argument("domain", nargs="+", help="one or more domains to analyze")
args = program.parse_args()

# Run domain through pipelines
for domain in args.domain:
    for pipeline in pipelines.names:
        pipelines.run(pipeline, domain)