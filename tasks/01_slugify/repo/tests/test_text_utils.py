from text_utils import slugify


def test_punctuation_collapses_to_single_hyphen():
    assert slugify("Hello, World!") == "hello-world"
