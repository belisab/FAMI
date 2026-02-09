# This script scrapes Wikipedia for Talk Pages and downloads those into a 
# folder. It makes a ton of requests to Wikipedia, so be aware - misusing this 
# script will probably get your device rate-limited.

import requests
from bs4 import BeautifulSoup, Tag
from typing import Any, cast
from pathlib import Path
import json
import time

headers = {
    # Lol
    "User-Agent": "NLP-Application Test SORRY-FOR-SO-MANY-REQUESTS"
}

def value_or_none(value: Tag | None) -> str | None:
    if not value:
        return None
    text = value.text.strip()
    return None if (text == "" or text == "\u2014N/a") else text

def scrape_page(url: str) -> str:
    full_url = f"https://en.wikipedia.org{url}"
    page = requests.get(full_url, headers=headers)
    if page.status_code != 200:
        raise Exception(f"failed to load wikipedia page {url}!!")
    
    return page.text

def scrape_list_page(list_data: dict[str, Any], url: str):
    full_url = f"https://en.wikipedia.org{url}"
    page = requests.get(full_url, headers=headers)
    if page.status_code != 200:
        raise Exception(f"failed to load {url}")

    soup = BeautifulSoup(page.text, "html.parser")
    for table in soup.find_all("table"):
        tbody = table.find("tbody")
        if not tbody:
            continue
        for tr in tbody.find_all("tr"):
            tds = tr.find_all("td")

            # Some cells span multiple columns; this splits those into 
            # the corresponding number of duplicates so we have a normalized 
            # amount of cells per row
            normalized_tds = list[Tag | None]()
            for td in tds:
                if "colspan" in td.attrs:
                    for _ in range(int(str(td["colspan"]))):
                        normalized_tds.append(td)
                else:
                    normalized_tds.append(td)
            
            if len(normalized_tds) == 0:
                continue

            while len(normalized_tds) < 7:
                normalized_tds.append(None)

            link_td = normalized_tds[0]
            assert link_td is not None
            link_a = link_td.find("a", href=True)
            year_td = normalized_tds[1]
            venue_td = normalized_tds[2]
            music_td = normalized_tds[3]
            lyrics_td = normalized_tds[4]
            book_td = normalized_tds[5]
            notes_td = normalized_tds[6]

            title = value_or_none(link_a if link_a else link_td)
            year_released = value_or_none(year_td)
            url = str(link_a["href"]) if link_a else ""

            # Generate an unique ID for this musical
            base_id = f"{title} {year_released if year_released else ''}"
            base_id = "".join(filter(
                lambda c: str.isalnum(c) or c == '-',
                base_id.lower().replace("  ", " ").strip().replace(" ", "-")
            ))

            # Add a counter to the end if there are multiple musicals with 
            # the same name
            id = base_id
            counter = 1
            while id in list_data:
                id = f"{base_id}-{counter}"
                counter += 1

            list_data[id] = {
                "title": title,
                "wikipedia_url": url if url.startswith("/wiki") else None,
                "year_released": year_released,
                "venue_type": value_or_none(venue_td),
                "music_by": value_or_none(music_td),
                "lyrics_by": value_or_none(lyrics_td),
                "book_by": value_or_none(book_td),
                "notes": value_or_none(notes_td),
            }
            print(f"found {title}")

musicals_json = Path("musicals.json")
musicals_pages = Path("../musical_wikipedia_pages/")

def scrape_list_pages():
    list_data = dict[str, Any]()
    scrape_list_page(list_data, "/wiki/List_of_musicals:_A_to_L")
    scrape_list_page(list_data, "/wiki/List_of_musicals:_M_to_Z")
    musicals_json.write_text(json.dumps(list_data, indent=4))

def scrape_pages():
    list_data = cast(dict[str, Any], json.loads(musicals_json.read_text()))
    musicals_pages.mkdir(exist_ok=True)

    # Fetch all musicals with URLs
    for id, musical in list_data.items():
        target_file = musicals_pages / f"{id}.html"
        if target_file.exists():
            print(f"[{id}] skipping (already fetched)")
            continue

        if musical["wikipedia_url"] is None:
            print(f"[{id}] skipping (no URL)")
            continue

        target_file.write_text(scrape_page(musical["wikipedia_url"]))

        print(f"[{id}] fetched {musical['wikipedia_url']} -> {target_file}")

        # Avoid spamming requests
        time.sleep(0.75)

scrape_list_pages()
scrape_pages()
