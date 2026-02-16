"""
theme_extraction.py
Extracts thematic tags (keyphrases) for each musical using PKE MultipartiteRank,
and saves them to: search_engine_project/static/musical_tags.json

Run from: FAMI/search_engine_project
    python theme_extraction.py
"""

import json
import os
import time
import re
import pke
import spacy

# Config
TOP_N = 5
MAX_CHARS = 8000  # limit text length to avoid very slow docs
FIELDS = ["description", "synopsis"]  # keep it light; add "songs" or "cast" if you want (slower)
SPACY_MODEL_NAME = "en_core_web_sm"

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SCRAPING_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..", "Week_4", "scraping")
)

META_PATH = os.path.join(SCRAPING_DIR, "musicals.json")
DATA_PATH = os.path.join(SCRAPING_DIR, "musicals-data.json")

OUT_PATH = os.path.join(BASE_DIR, "static", "musical_tags.json")



def clean_text(s: str) -> str:
    """Basic cleanup to reduce weird tokenizer issues."""
    s = s or "" # handle None
    s = s.replace("\u00a0", " ")  # non-breaking space 
    s = re.sub(r"\s+", " ", s).strip() # collapse whitespace
    return s

# Build a single text blob from selected fields, cleaned and truncated.
def build_text(musical: dict) -> str:
    """Concatenate selected fields and truncate."""
    parts = []
    for field in FIELDS:
        if musical.get(field):
            parts.append(str(musical[field]))
    text = " ".join(parts)
    text = clean_text(text)
    return text[:MAX_CHARS]

# Extract keywords using PKE MultipartiteRank. Returns list of phrases (no scores).
def extract_keywords(text: str, spacy_nlp, top_n: int = TOP_N):
    """Run PKE MultipartiteRank and return list of phrases (no scores)."""
    extractor = pke.unsupervised.MultipartiteRank()

    # IMPORTANT: pass the *nlp object*, not a string
    extractor.load_document(input=text, language="en", spacy_model=spacy_nlp)

    # Candidate selection: nouns/proper nouns/adjectives are good for "tags"
    extractor.candidate_selection(pos={"NOUN", "PROPN", "ADJ"})

    # Candidate weighting
    extractor.candidate_weighting(alpha=1.1, threshold=0.75, method="average")

    # Get best phrases
    keyphrases = extractor.get_n_best(n=top_n)  # [(phrase, score), ...]
    return [phrase for phrase, _score in keyphrases]


def main():
    if not os.path.exists(META_PATH):
        raise FileNotFoundError(f"Metadata JSON not found: {META_PATH}")

    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Input JSON not found: {DATA_PATH}")


    # Load spaCy once (huge speedup + fixes your tokenizer error)
    try:
        nlp = spacy.load(SPACY_MODEL_NAME)
    except OSError:
        raise OSError(
            f"spaCy model '{SPACY_MODEL_NAME}' not found.\n"
            f"Install it with:\n"
            f"  python -m spacy download {SPACY_MODEL_NAME}"
        )

    # Load musicals data
    with open(META_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        pagedata = json.load(f)

    # Resume support: if output exists, keep what you've already done
    if os.path.exists(OUT_PATH):
        try:
            with open(OUT_PATH, "r", encoding="utf-8") as f:
                tags_by_title = json.load(f)
        except Exception:
            tags_by_title = {}
    else:
        tags_by_title = {}

    items = list(metadata.items())
    total = len(items)

    start_all = time.time()
    processed_now = 0

    print(f"Input:  {DATA_PATH}")
    print(f"Output: {OUT_PATH}")
    print(f"Total musicals: {total}")
    print(f"Fields: {FIELDS} | TOP_N={TOP_N} | MAX_CHARS={MAX_CHARS}")
    print("-" * 60)

    try:
        for i, (musical_id, meta) in enumerate(items, start=1):
            title = clean_text(meta.get("title", ""))

            musical = pagedata.get(musical_id, {})


            if not title:
                continue

            # skip if already done
            if title in tags_by_title:
                continue

            print(f"[{i}/{total}] Processing: {title}")

            text = build_text(musical)
            if not text:
                tags_by_title[title] = []
            else:
                try:
                    tags = extract_keywords(text, spacy_nlp=nlp, top_n=TOP_N)
                    tags_by_title[title] = tags
                except Exception as e:
                    print(f"  -> ERROR on '{title}': {type(e).__name__}: {e}")
                    tags_by_title[title] = []

            processed_now += 1

            # checkpoint every 10 items (change to 1 if you want max safety)
            if processed_now % 10 == 0:
                with open(OUT_PATH, "w", encoding="utf-8") as f:
                    json.dump(tags_by_title, f, ensure_ascii=False, indent=2)
                print("  (checkpoint saved)")

        # final save
        with open(OUT_PATH, "w", encoding="utf-8") as f:
            json.dump(tags_by_title, f, ensure_ascii=False, indent=2)

    except KeyboardInterrupt:
        print("\nInterrupted. Saving progress...")
        with open(OUT_PATH, "w", encoding="utf-8") as f:
            json.dump(tags_by_title, f, ensure_ascii=False, indent=2)
        print("Progress saved.")
        raise

    elapsed = time.time() - start_all
    print("-" * 60)
    print(f"Done. Saved to {OUT_PATH}")
    print(f"Elapsed: {elapsed:.1f}s")

if __name__ == "__main__":
    main()



