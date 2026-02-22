from sklearn.feature_extraction.text import CountVectorizer
#from bs4 import BeautifulSoup
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
#from algorithms.doc import SearchableDocument
from typing import Sequence, List




class TfIdfSearchEngine:
    documents: List[str]
    tf_matrix: np.ndarray
    t2i: dict
    tokenizer: callable
    def __init__(self, documents: Sequence[str]):
        self.documents = [str(doc) for doc in documents]

        self.text = [str(doc) for doc in self.documents]

        self.tfidf = TfidfVectorizer(
            lowercase=True,
            sublinear_tf=True,
            use_idf=True,
            norm="l2"
        )

        #transpose matrix
        self.tf_matrix = self.tfidf.fit_transform(self.text).T.todense()
        #t2i and tokenizer
        self.t2i = self.tfidf.vocabulary_
        self.tokenizer = self.tfidf.build_tokenizer()

    # Query function using SearcableDocument
    def search_tfidf(self, query: str, top_k: int = 5) -> List[str]:

        query = query.lower()
        tokens = self.tokenizer(query)
        hits = np.zeros(self.tf_matrix.shape[1])

        for t in tokens:
            if t in self.t2i:
                hits += np.array(self.tf_matrix[self.t2i[t]])[0]
        print("tokens", tokens)
        print("tokens in vocab", [t for t in tokens if t in self.t2i])

        hits_and_doc_ids = [(hits[i], i) for i in range(len(hits)) if
                        hits[i] > 0]
        ranked_hits_and_doc_ids = sorted(hits_and_doc_ids, reverse=True)

        return [
            self.documents[i]
            for score, i in ranked_hits_and_doc_ids[:top_k]
        ]


        









    


   

   
   
    
    

    






