from pipelines import ScrapePipeline, ExtractPipeline, LangDetectPipeline

for domain in ["17ziele.de"]:
    ScrapePipeline.process(domain)
    ExtractPipeline.process(domain)
    LangDetectPipeline.process(domain)