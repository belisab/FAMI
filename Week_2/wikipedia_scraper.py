# This script scrapes Wikipedia for Talk Pages and downloads those into a 
# folder. It makes a ton of requests to Wikipedia, so be aware - misusing this 
# script will probably get your device rate-limited.

import time
import requests
from bs4 import BeautifulSoup
import os

# !!!! Make sure this is False when committing !!!!
DO_RUN_THIS_FILE = False
# Page to start from, expressed as the URL subpath (for example this one leads 
# to https://en.wikipedia.org/wiki/Cat)
INITIAL_PAGE = "/wiki/Cat"
# How many subpages the scraper will find. Do note that this represents 
# exponential orders-of-magnitude mega infinity growth - incrementing by just 
# one might change the runtime of the script from a few hours to a few weeks!
MAX_DEPTH = 2

headers = {
    # Lol
    "User-Agent": "NLP-Application Test SORRY-FOR-SO-MANY-REQUESTS"
}

# Scrape a given Wikipedia page from its URL
def recursively_scrape_page(relative_url: str, remaining_depth: int) -> set[str]:
    results = set[str]()

    if remaining_depth <= 0:
        return results
    
    # `relative_url` is in the format `/wiki/{page}`
    page_url = f"https://en.wikipedia.org{relative_url}"

    print(f"fetching {page_url}")

    try:
        page_data = requests.get(page_url, headers=headers)
        if page_data.status_code == 200:
            # Parse HTML page using BeautifulSoup
            soup = BeautifulSoup(page_data.text, "html.parser")
            # Some Wikipedia pages may be redirects; this figures out what the 
            # actual URL of the page is by searching for the "canonical" link
            # contained within the page metadata
            if real_url := soup.find("a", attrs={'rel':'canonical', 'href':True}):
                results.add(str(real_url["href"]))

            # Iterate through all of the links on the page (including only the 
            # ones that point to other Wikipedia articles, aka ones starting 
            # with a relative URL `/wiki/`), check if they haven't been scraped 
            # already, and if they haven't, scrape 'em!
            for link in [
                str(a['href'])
                for a 
                in soup.find_all("a", href=True)
                if str(a["href"]).startswith("/wiki/")
            ]:
                # Skip pages we have already checked
                if link not in results:
                    results.update(recursively_scrape_page(link, remaining_depth - 1))
        else:
            print(f"failed to get {page_url}: {page_data.status_code}")
    # We don't really care about errors, just continue chugging along
    except requests.exceptions.MissingSchema:
        pass
    except requests.exceptions.InvalidSchema:
        pass
    
    return results

def do_scrape_links():
    results = recursively_scrape_page(INITIAL_PAGE, MAX_DEPTH)
    with open("wikipedia_talk_page_links.txt", "w") as f:
        f.write("\n".join(results))

def do_scrape_talk_pages():
    if not os.path.exists("wikipedia_talk_pages/"):
        os.makedirs("wikipedia_talk_pages/")
    
    with open("wikipedia_talk_page_links.txt", "r") as f:
        for url in f.read().splitlines():

            parts = url.rsplit('/', 1)
            if ":" in parts[1]:
                continue

            talk_url = f"{parts[0]}/Talk:{parts[1]}"
            print(f"scraping {talk_url}")
            try:
                data = requests.get(talk_url, headers=headers)
                with open(f"wikipedia_talk_pages/{parts[1]}.html", "w") as f2:
                    f2.write(data.text)
                time.sleep(1)
            except requests.exceptions.MissingSchema:
                pass
            except requests.exceptions.InvalidSchema:
                pass

if not DO_RUN_THIS_FILE:
    print(
        "NOTE: Running this Python file will take *forever* and might get you \n\
        rate-limited on Wikipedia. Change the variable DO_RUN_TIHS_FILE to True \n\
        within its code if you are sure about running it."
    )
else:
    print("Lycka till och ha en jätterolig tid :-)")
    do_scrape_links()
    do_scrape_talk_pages()
