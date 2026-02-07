
### This file takes the pages that have been downloaded by 
### `musicals_list_scraper.py` and extracts the relevant page data out of them
### (So we don't have a billion raw HTML pages again)

from pathlib import Path
from bs4 import BeautifulSoup, Tag
import typing
import json
import re

def extract_only_text(p: Tag) -> str:
    # Remove citations
    for a in p.find_all("a", {
        "href": lambda x: x.startswith("#cite") # type: ignore
    }):
        a.extract()
    return p.get_text(" ", strip=True)

def find_content_text(start: Tag, include_start: bool = False) -> str:
    result = ""
    if include_start:
        result += extract_only_text(start) + "\n\n"

    for sib in start.next_siblings:
        if not isinstance(sib, Tag):
            continue

        classes = sib.attrs["class"] if "class" in sib.attrs else ""
        
        if "mw-heading2" in classes:
            break

        if "navigation-not-searchable" in classes:
            continue

        if "mw-heading3" in classes:
            h3 = sib.find('h3')
            assert h3 is not None
            result += f"### {h3.text}\n\n"
        elif sib.name == "p":
            result += extract_only_text(sib) + "\n\n"
    
    return result.strip()

def find_content_by_header(classes: list[str]) -> str | None:
    if h2 := soup.find("h2", { "id": lambda i: i.lower() in classes if i else False }):
        assert h2.parent is not None
        return find_content_text(h2.parent)
    return None

def normalize_str(a: str) -> str:
    return a.lower().strip().replace(" ", "")

musicals_data = typing.cast(list[typing.Any], json.loads(Path("./musicals.json").read_text()))

result: dict[int, typing.Any] = dict()
for enum_index, path in enumerate(Path("../musical_wikipedia_pages/").glob("*.html")):
    # if enum_index > 50:
    #     break

    index = re.search(r"\d+", path.name)
    assert index is not None # ihatepylanceihatepylanceihatepylanceihatepylanceihatepylance
    index = int(index.group(0))

    print(f"[{enum_index}] processing {path} ({musicals_data[index]['wikipedia_url']})")

    # `html.parser` parses the page wrong :(
    # To be more precise, Wikipedia for some reason has <meta .. /> tags in the 
    # middle of content, which cause `html.parser` to trip up
    soup = BeautifulSoup(path.read_text(), "html5lib")

    title = soup.find("h1", { "id": "firstHeading" })
    assert title is not None

    wiki_link = soup.find("link", { "rel": "canonical", "href": True })
    assert wiki_link is not None
    canonical_wiki_url = str(wiki_link["href"])
    canonical_wiki_url = canonical_wiki_url.removeprefix("https://en.wikipedia.org")

    content_soup = soup.find("div", { "class": "mw-content-ltr" })
    assert content_soup is not None

    first_desc_paragraph = None
    for sib in content_soup.children:
        if not isinstance(sib, Tag):
            continue

        if sib.name == "p":
            first_desc_paragraph = sib
            break
    
    assert first_desc_paragraph is not None

    description = find_content_text(first_desc_paragraph, include_start=True)

    # Also known as the plot or story
    synopsis = find_content_by_header(["synopsis", "plot"])
    cast = find_content_by_header(["cast", "original_casts", "cast_and_characters"])
    songs = find_content_by_header(["musical_numbers", "songs", "song_list"])

    result[index] = {
        "title": title.text,
        "description": description,
        "synopsis": synopsis,
        "cast": cast,
        "songs": songs,
        "canonical_url": canonical_wiki_url,
    }

Path("musicals-data.json").write_text(json.dumps(result, indent=4))
