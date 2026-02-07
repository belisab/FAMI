# This script scrapes Wikipedia for Talk Pages and downloads those into a 
# folder. It makes a ton of requests to Wikipedia, so be aware - misusing this 
# script will probably get your device rate-limited.

import requests
from bs4 import BeautifulSoup
from typing import Any, cast
from pathlib import Path
import json
import time

headers = {
    # Lol
    "User-Agent": "NLP-Application Test SORRY-FOR-SO-MANY-REQUESTS"
}

def value_or_none(value: str) -> str | None:
    value = value.strip()
    return None if (value == "" or value == "\u2014N/a") else value

def scrape_page(url: str) -> str:
    full_url = f"https://en.wikipedia.org{url}"
    page = requests.get(full_url, headers=headers)
    if page.status_code != 200:
        raise Exception(f"failed to load wikipedia page {url}!!")
    
    return page.text

def scrape_list_page(url: str) -> list[Any]:
    full_url = f"https://en.wikipedia.org{url}"
    page = requests.get(full_url, headers=headers)
    if page.status_code != 200:
        raise Exception(f"failed to load {url}")

    list_data: list[Any] = list()

    soup = BeautifulSoup(page.text, "html.parser")
    for table in soup.find_all("table"):
        tbody = table.find("tbody")
        if not tbody:
            continue
        for tr in tbody.find_all("tr"):
            try:
                link_td, year_td, venue_td, music_td, lyrics_td, book_td, notes_td = tr.find_all("td")
                link_a = link_td.find("a", href=True)
                url = str(link_a["href"]) if link_a else ""
                list_data.append({
                    "title": value_or_none(link_a.text if link_a else link_td.text),
                    "wikipedia_url": value_or_none(url if url.startswith("/wiki") else ""),
                    "year_released": value_or_none(year_td.text),
                    "venue_type": value_or_none(venue_td.text),
                    "music_by": value_or_none(music_td.text),
                    "lyrics_by": value_or_none(lyrics_td.text),
                    "book_by": value_or_none(book_td.text),
                    "notes": value_or_none(notes_td.text),
                })
                print(f"found {list_data[-1]['title']}")
            except ValueError:
                pass
    
    return list_data

musicals_json = Path("musicals.json")
musicals_pages = Path("../musical_wikipedia_pages/")

def scrape_list_pages():
    list_data = list[Any]()
    list_data += scrape_list_page("/wiki/List_of_musicals:_A_to_L")
    list_data += scrape_list_page("/wiki/List_of_musicals:_M_to_Z")
    musicals_json.write_text(json.dumps(list_data, indent=4))

def scrape_pages():
    list_data = cast(list[Any], json.loads(musicals_json.read_text()))
    musicals_pages.mkdir(exist_ok=True)

    # Fetch all musicals with URLs
    for i, musical in enumerate(list_data):
        target_file = musicals_pages / f"{i}.html"
        if target_file.exists():
            print(f"[{i+1}/{len(list_data)}] skipping (already fetched)")
            continue

        if musical["wikipedia_url"] is None:
            print(f"[{i+1}/{len(list_data)}] skipping (no URL)")
            continue

        target_file.write_text(scrape_page(musical["wikipedia_url"]))

        print(f"[{i+1}/{len(list_data)}] fetched {musical['wikipedia_url']}")

        # Avoid spamming requests
        time.sleep(0.75)

scrape_list_pages()
scrape_pages()
