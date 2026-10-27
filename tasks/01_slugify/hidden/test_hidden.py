from text_utils import slugify


def test_basic():
    assert slugify("Hello, World!") == "hello-world"


def test_spaces_and_edges():
    assert slugify("  Many   spaces  ") == "many-spaces"


def test_existing_hyphens():
    assert slugify("a--b") == "a-b"
    assert slugify("Already-slug") == "already-slug"
