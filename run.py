import argparse

program = argparse.ArgumentParser(
    description="Run one or several domains through all pipelines",
    epilog="Example: python ./run.py example.com test.com",
)
program.add_argument("domain", nargs="+", help="one or more domains to analyze")
args = program.parse_args()

for domain in args.domain:
    # Load pipelines only when needed, otherwise run.py --help becomes very slow
    pipelines = __import__("pipelines")

    # Run domain through pipelines
    pipelines.ScrapePipeline.process(domain)
    pipelines.ExtractPipeline.process(domain)
    pipelines.LangDetectPipeline.process(domain)
    pipelines.KeywordPipeline.process(domain)
