from pipelines import ScrapePipeline

for domain in ["17ziele.de"]:
    ScrapePipeline.process(domain)
