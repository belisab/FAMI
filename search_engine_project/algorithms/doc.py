
from abc import abstractmethod

class SearchableDocument:
    @abstractmethod
    def get_searchable_data(self) -> str:
        pass
