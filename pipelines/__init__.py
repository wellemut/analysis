import importlib

# Define the pipeline names and the associated modules/classes
pipelines = {
    "scrape": "ScrapePipeline",
    "extract": "ExtractPipeline",
    "langdetect": "LangDetectPipeline",
    "keyword": "KeywordPipeline",
    "links": "LinksPipeline",
    "socials": "SocialsPipeline",
}

# Names of available pipelines
names = list(pipelines.keys())

# Run a pipeline with the given name for a given domain
def run(name, domain):
    # Load the pipeline (dynamically, for performance reasons)
    pipeline_name = pipelines.get(name)
    module = importlib.import_module(f".{pipeline_name}", __name__)
    pipeline_class = getattr(module, pipeline_name)

    # Run the pipeline
    pipeline_class.process(domain)