from helpers.extractors import BaseExtractor


class ExampleExtractor(BaseExtractor):
    @classmethod
    def extract(cls, link):
        if not link.startswith("test:"):
            return None

        return link.replace("test:", "", 1)


def test_it_adds_items_once_per_page():
    extractor = ExampleExtractor()
    extractor.process("test:abc", 1)
    extractor.process("test:abc", 1)
    extractor.process("test:abc", 2)

    assert extractor.counts["abc"] == 2


def test_it_does_not_count_items_when_none():
    extractor = ExampleExtractor()
    extractor.process("abc", 1)
    extractor.process("def", 1)

    assert len(extractor.counts.keys()) == 0


def test_each_instance_tracks_its_own_handles():
    e1 = ExampleExtractor()
    e2 = ExampleExtractor()

    e1.process("test:abc", 1)

    assert e1.counts["abc"] == 1
    assert len(e2.counts.keys()) == 0