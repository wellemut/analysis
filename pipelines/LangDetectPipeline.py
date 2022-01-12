import os
import fasttext
from models import TextBlock, Website
from helpers import batches, suppress_stdout_and_stderr
from config import APPLICATION_DATA_PATH


class LangDetectPipeline:
    model = None
    # Path to the pre-trained fasttext model (downloaded in Dockerfile)
    PRETRAINED_MODEL_PATH = os.path.join(APPLICATION_DATA_PATH, "lid.176.bin")
    # Threshold above which the language prediction is considered reliable
    # This is lower than Google's 0.7 threshold (https://github.com/google/cld3/blob/fc486d014fb9043f3ec2950fb9829e8ca844cb45/src/nnet_language_identifier.cc#L67),
    # but in our testing, 0.5 seems to perform decently well
    PREDICTION_RELIABILITY_THRESHOLD = 0.5

    @classmethod
    def process(cls, domain):
        website = Website.find_by(domain=domain)

        # Get IDs for all text blocks that belong to this domain
        block_ids = TextBlock.query.filter_by(website=website).ids()

        # Operate on text blocks in batches for better performance
        with TextBlock.session.begin():
            for ids in batches(block_ids, 100):
                # Load the blocks in this batch
                blocks = TextBlock.query.where(TextBlock.id.in_(ids)).all()

                # Identify language for each block
                for block in blocks:
                    block.language = cls.detect_language(block.content)

                # Save the updated text blocks
                for block in blocks:
                    block.save()

    @classmethod
    def detect_language(cls, text):
        # Load model (if not loaded yet)
        if cls.model is None:
            # Suppress very old message about model change
            # See: https://github.com/facebookresearch/fastText/commit/9ef22d9fac33c84480fa2e4edf56df13cb0bcfbb
            with suppress_stdout_and_stderr():
                cls.model = fasttext.load_model(cls.PRETRAINED_MODEL_PATH)

        # Predict the language for the given text
        prediction = cls.model.predict(text)
        language = prediction[0][0].replace("__label__", "")
        probability = prediction[1][0]

        # If the prediction probability lies below our threshold, set the
        # language to 'unclear'
        if probability <= cls.PREDICTION_RELIABILITY_THRESHOLD:
            return "unclear"

        return language
