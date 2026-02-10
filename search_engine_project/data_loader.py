import json
import os
from pathlib import Path
from algorithms.doc import SearchableDocument
from dataclasses import dataclass
from markdown import markdown

@dataclass
class Musical(SearchableDocument):
    index: int
    title: str
    year_released: str
    venue_type: str | None
    synopsis: str | None
    description: str | None
    cast: str | None
    songs: str | None

    def get_searchable_data(self) -> str:
        return f"{self.title} ({self.venue_type} {self.year_released})\n\n" + (
            f"{self.description}\n\n{self.synopsis}\n\n{self.cast}\n\n{self.songs}"
        )

    def render_synopsis(self) -> str | None:
        return markdown(self.synopsis) if self.synopsis else None

def load_documents() -> list[Musical]:
    base_dir = Path(os.path.dirname(os.path.abspath(__file__))) / ".." / "Week_4" / "scraping"
    metadata = json.loads((base_dir / "musicals.json").read_text())
    pagedata = json.loads((base_dir / "musicals-data.json").read_text())

    # I changed this so meta is a callable dictionary
    musicals: list[Musical] = []
    for index, (musical_id, meta) in enumerate(metadata.items()):
        data = pagedata.get(musical_id, {})
        musicals.append(Musical(
            index=index,
            title=meta.get("title",""),
            year_released=meta.get("year_released", ""),
            venue_type=meta.get("venue_type", None),
            synopsis=data.get("synopsis") if data else None,
            description=data.get("description") if data else None,
            cast=data.get("cast") if data else None,
            songs=data.get("songs") if data else None,
        ))

    return musicals

