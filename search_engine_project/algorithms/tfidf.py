import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from algorithms.doc import SearchableDocument
from typing import Any, Generic, Sequence, List, TypeVar

T = TypeVar('T', bound=SearchableDocument)

class TfIdfSearchEngine(Generic[T]):
    documents: Sequence[T]
    text: list[str]
    tdidf: TfidfVectorizer
    tf_matrix: Any
    t2i: Any
    tokenizer: Any

    def __init__(self, documents: Sequence[T]):
        self.documents = list(documents)
        self.text = [doc.get_searchable_data() for doc in self.documents]
        self.tfidf = TfidfVectorizer(
            lowercase=True,
            sublinear_tf=True,
            use_idf=True,
            norm="l2"
        )

        # transpose matrix
        self.tf_matrix = self.tfidf.fit_transform(self.text).T.todense() # type: ignore
        # t2i and tokenizer
        self.t2i = self.tfidf.vocabulary_ # type: ignore
        self.tokenizer = self.tfidf.build_tokenizer() # type: ignore

    # Query function using SearcableDocument
    def search(self, query: str, top_k: int = 5) -> List[T]:
        query = query.lower()
        tokens = self.tokenizer(query)
        hits = np.zeros(self.tf_matrix.shape[1])

        for t in tokens:
            if t in self.t2i:
                hits += np.array(self.tf_matrix[self.t2i[t]])[0]

        hits_and_doc_ids = [(hits, i) for i, hits in enumerate(hits) if
                        hits > 0]
        ranked_hits_and_doc_ids = sorted(hits_and_doc_ids, reverse=True)

        return [
            self.documents[i]
            for _hits, i in ranked_hits_and_doc_ids[:top_k]
        ]
