
### This file implements a general Boolean search component that can be imported 
### by later projects without having to rewrite Boolean search again.

from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from scipy import sparse
import typing

OPERATORS = {
    "and": "&",
    "or":  "|",
    "not": "1 - ",
    "(":   "(",
    ")":   ")",
}

def rewrite_query(query: str):
    return " ".join(
        # If the search term exists in our dictionary of operators, get it, 
        # otherwise find occurrences of the term in `td_matrix``. If the term 
        # is not in our dictionary, then the query results in 0 (since the 
        # term does not occur in any of the documents)
        OPERATORS.get(t, f'(self.td_matrix[self.t2i["{t}"]] if "{t}" in self.t2i else empty_row)')
        for t in query.split()
    )

class BooleanSearchEngine:
    documents: list[str]
    td_matrix: typing.Any
    t2i: typing.Any

    def __init__(self, documents: list[str]) -> None:
        self.documents = documents
        cv = CountVectorizer(lowercase=True, binary=True)

        sparse_matrix = typing.cast(sparse.spmatrix, cv.fit_transform(documents)) # type: ignore
        dense_matrix = sparse_matrix.todense()
        self.td_matrix = dense_matrix.T
        self.t2i = cv.vocabulary_ # type: ignore

    def search(self, query: str) -> list[str]:
        query = query.lower().strip()
        if query == "":
            return []
        
        # Generate a row of all zeroes for queries containing words not in our 
        # dictionary
        empty_row = np.matrix(np.repeat(0, self.td_matrix.shape[1])) # type: ignore
        rewritten = rewrite_query(query)

        # Eval runs the string as a Python command
        # `td_matrix`, `t2i`, and `empty_row` have to be in scope in 
        # order for eval() to work
        eval_result = eval(rewritten)

        # Finding the matching document
        hits_matrix = eval_result
        hits_list = list(hits_matrix.nonzero()[1])

        return [self.documents[doc_idx] for doc_idx in hits_list]
