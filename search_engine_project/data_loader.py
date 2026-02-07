import json
import os

def load_documents():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    data_path = os.path.abspath(
        os.path.join(base_dir, "..", "Week_4", "scraping", "musicals-data.json")
    )

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents = []
    metadata = []

    for _, musical in data.items():
        text_parts = []

        for field in ["title", "description", "synopsis", "cast", "songs"]:
            if musical.get(field):
                text_parts.append(musical[field])

        documents.append("\n".join(text_parts))
        metadata.append({
            "title": musical.get("title"),
            "url": musical.get("canonical_url")
        })

    return documents, metadata
