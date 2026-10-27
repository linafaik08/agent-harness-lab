import re


def slugify(title: str) -> str:
    """Turns a title into a lowercase, hyphen-separated URL slug."""
    slug = re.sub(r"[^a-z0-9]", "-", title.lower())
    return slug
