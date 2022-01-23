import pytest
from helpers import matches_dict
from helpers.extractors import BaseExtractor


class ExampleExtractor(BaseExtractor):
    @classmethod
    def extract(cls, link):
        if not link.startswith("test:"):
            return None

        return link.replace("test:", "", 1)


def describe_results():
    def it_adds_items_once_per_page():
        extractor = ExampleExtractor(domain="test.com", page_count=5)
        extractor.process("test:abc", link_id=1, page_id=1)
        extractor.process("test:abc", link_id=2, page_id=1)
        extractor.process("test:abc", link_id=3, page_id=2)

        assert len(extractor.results) == 1
        assert dict(
            handle="abc", link_count=3, page_count=2, frequency=2 / 5
        ) == matches_dict(extractor.results[0])

    def it_does_not_count_items_when_none():
        extractor = ExampleExtractor(domain="test.com", page_count=5)
        extractor.process("abc", link_id=1, page_id=1)
        extractor.process("def", link_id=2, page_id=1)

        assert len(extractor.results) == 0

    def it_sets_frequency_to_false_when_page_count_is_zero():
        extractor = ExampleExtractor(domain="test.com", page_count=0)
        extractor.process("test:abc", link_id=1, page_id=1)

        assert len(extractor.results) == 1
        assert dict(
            handle="abc", link_count=1, page_count=1, frequency=False
        ) == matches_dict(extractor.results[0])


def describe_counts():
    def it_adds_items_once_per_page():
        extractor = ExampleExtractor(domain="test.com", page_count=5)
        extractor.process("test:abc", link_id=1, page_id=1)
        extractor.process("test:abc", link_id=2, page_id=1)
        extractor.process("test:abc", link_id=3, page_id=2)

        assert extractor.counts["abc"] == 2

    def it_does_not_count_items_when_none():
        extractor = ExampleExtractor(domain="test.com", page_count=5)
        extractor.process("abc", link_id=1, page_id=1)
        extractor.process("def", link_id=2, page_id=1)

        assert len(extractor.counts.keys()) == 0

    def each_instance_tracks_its_own_handles():
        e1 = ExampleExtractor(domain="test.com", page_count=5)
        e2 = ExampleExtractor(domain="abc.com", page_count=5)

        e1.process("test:abc", link_id=1, page_id=1)

        assert e1.counts["abc"] == 1
        assert len(e2.counts.keys()) == 0


def describe_top_candidate():
    # Simplify the extract method, so that it returns the same value as we put
    # into it. This is fine for these tests, as we already test the real extract
    # method above.
    @pytest.fixture(autouse=True)
    def mock_extract(mocker):
        mocker.patch.object(ExampleExtractor, "extract", lambda cls, x: x)

    # Test helper to mock the processing/extraction of many handles
    def _process_many(extractor, handle, times):
        for num in range(times):
            extractor.process(handle, link_id=num, page_id=num)

    def describe_when_no_extractions():
        def it_returns_none():
            e = ExampleExtractor(domain="test.com", page_count=20)
            assert e.top_candidate == None

    def describe_when_one_extraction():
        def it_returns_handle_used_on_at_least_half_the_pages():
            e = ExampleExtractor(domain="test.com", page_count=20)
            _process_many(e, "helloco", 10)
            assert e.top_candidate == "helloco"

        def it_returns_handle_with_80_perc_similarity_to_domain():
            e = ExampleExtractor(domain="test.com", page_count=20)
            _process_many(e, "testco", 1)
            assert e.top_candidate == "testco"

        def it_returns_none_otherwise():
            e = ExampleExtractor(domain="test.com", page_count=20)
            _process_many(e, "helloco", 9)
            _process_many(e, "teeeeeest", 1)
            assert e.top_candidate == None

    def describe_when_multiple_extractions():
        def it_returns_most_used_handle_if_used_five_times_as_much_as_others():
            e = ExampleExtractor(domain="test.com", page_count=20)
            _process_many(e, "testcom", 3)
            _process_many(e, "helloco", 16)
            assert e.top_candidate == "helloco"

        def it_returns_most_used_handle_if_it_is_also_most_similar():
            e = ExampleExtractor(domain="test.com", page_count=20)
            _process_many(e, "teest", 5)
            _process_many(e, "testtest", 4)
            assert e.top_candidate == "teest"

        def it_returns_none_otherwise():
            e = ExampleExtractor(domain="test.com", page_count=20)
            _process_many(e, "helloco", 16)
            _process_many(e, "testcom", 5)
            assert e.top_candidate == None