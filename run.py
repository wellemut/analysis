from pipelines import (
    ScrapePipeline,
    ExtractPipeline,
    LangDetectPipeline,
    KeywordPipeline,
)

for domain in ["17ziele.de"]:
    ScrapePipeline.process(domain)
    ExtractPipeline.process(domain)
    LangDetectPipeline.process(domain)
    KeywordPipeline.process(domain)