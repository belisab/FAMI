
### This file implements a general Boolean search component that can be imported 
### by later projects without having to rewrite Boolean search again.

from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from scipy import sparse
import typing
from typing import Sequence
import fnmatch
from algorithms.doc import SearchableDocument

OPERATORS = {
    "and": "&",
    "or":  "|",
    "not": "1 - ",
    "(":   "(",
    ")":   ")",
}

KGramIndex = dict[str, set[str]]

# k-gram index functions
def build_kgram_index(vocabulary: list[str], k: int = 3) -> KGramIndex:
    index: KGramIndex = {}
    for term in vocabulary:
        padded = f"${term}$"
        for i in range(len(padded) - k + 1):
            kgram = padded[i:i+k]
            index.setdefault(kgram, set()).add(term)
    return index

# Extract k-grams from wildcard pattern
def kgrams_from_wildcard(pattern: str, k: int = 3) -> list[str]:
    parts = pattern.split("*")
    kgrams: list[str] = []

    # start
    if parts[0] != "":
        kgrams.append("$" + parts[0][:k-1])

    # end
    if parts[-1] != "":
        kgrams.append(parts[-1][-k+1:] + "$")

    return kgrams

# Expand wildcard pattern using k-gram index
def expand_wildcard(pattern: str, kgram_index: KGramIndex, vocabulary: list[str]) -> list[str]:
    kgrams = kgrams_from_wildcard(pattern)
    if not kgrams:
        return []

    candidates = None
    for kg in kgrams:
        if kg not in kgram_index:
            return []
        if candidates is None:
            candidates = kgram_index[kg].copy()
        else:
            candidates &= kgram_index[kg]
    
    assert candidates is not None

    # post-filtering
    return [t for t in candidates if fnmatch.fnmatch(t, pattern)]

# Expand wildcards in the entire query
def expand_wildcards_in_query(query: str, kgram_index: KGramIndex, vocabulary: list[str]) -> str:
    tokens = query.split()
    new_tokens: list[str] = []

    for t in tokens:
        if "*" in t or "?" in t:
            expanded = expand_wildcard(t, kgram_index, vocabulary)
            if expanded:
                new_tokens.append("(" + " or ".join(expanded) + ")")
            else:
                new_tokens.append("( )")  # no match
        else:
            new_tokens.append(t)

    return " ".join(new_tokens)

def rewrite_query(query: str):
    return " & ".join(
        # If the search term exists in our dictionary of operators, get it, 
        # otherwise find occurrences of the term in `td_matrix``. If the term 
        # is not in our dictionary, then the query results in 0 (since the 
        # term does not occur in any of the documents)
        OPERATORS.get(t, f'(self.td_matrix[self.t2i["{t}"]] if "{t}" in self.t2i else empty_row)')
        for t in query.split()
    )

class BooleanSearchEngine:
    documents: Sequence[SearchableDocument]
    td_matrix: typing.Any
    t2i: typing.Any
    kgram_index: KGramIndex | None

    def __init__(self, documents: Sequence[SearchableDocument], support_wildcards: bool = True) -> None:
        self.documents = documents
        cv = CountVectorizer(lowercase=True, binary=True)

        sparse_matrix = typing.cast(
            sparse.spmatrix,
            cv.fit_transform( # type: ignore
                [doc.get_searchable_data() for doc in documents]
            )
        )
        dense_matrix = sparse_matrix.todense()
        self.td_matrix = dense_matrix.T
        self.t2i = cv.vocabulary_ # type: ignore
        self.kgram_index = build_kgram_index(self.t2i.keys()) if support_wildcards else None

    def search(self, query: str) -> list[SearchableDocument]:
        query = query.lower().strip()
        if query == "":
            return []
        
        # Generate a row of all zeroes for queries containing words not in our 
        # dictionary
        empty_row = np.matrix(np.repeat(0, self.td_matrix.shape[1])) # type: ignore
        expanded = expand_wildcards_in_query(query, self.kgram_index, self.t2i.keys()) if self.kgram_index else query
        rewritten = rewrite_query(expanded)

        # Eval runs the string as a Python command
        # `td_matrix`, `t2i`, and `empty_row` have to be in scope in 
        # order for eval() to work
        eval_result = eval(rewritten)

        # Finding the matching document
        hits_matrix = eval_result
        hits_list = list(hits_matrix.nonzero()[1])

        return [self.documents[doc_idx] for doc_idx in hits_list]
