
import gensim # type: ignore
from gensim.models.keyedvectors import KeyedVectors # type: ignore
import gensim.downloader as gsapi # type: ignore
import typing

# Based on https://github.com/Helsinki-NLP/neural-search-tutorials/blob/main/average_word_vectors.ipynb

class SemanticSearchEngine:
    documents: list[str]
    doc_vectors: KeyedVectors
    ft: typing.Any

    def into_wordvec(self, text: str) -> typing.Any:
        text_without_stopwords = gensim.parsing.preprocessing.remove_stopwords(text) # type: ignore
        tokens = gensim.utils.simple_preprocess(text_without_stopwords) # type: ignore
        return self.ft.get_mean_vector(tokens)

    def __init__(self, documents: list[str]) -> None:
        print("Loading dataset, this will take a while")
        self.ft = gsapi.load("fasttext-wiki-news-subwords-300") # type: ignore
        self.documents = documents
        self.doc_vectors = KeyedVectors(self.ft.vector_size, count=len(documents))
        for i, doc in enumerate(documents):
            dv = self.into_wordvec(doc)
            self.doc_vectors.add_vector(i, dv) # type: ignore

    def search(self, query: str) -> list[str]:
        q = self.into_wordvec(query)
        most_sim = self.doc_vectors.most_similar([q], topn=5) # type: ignore

        for doc_position, doc_score in most_sim: # type: ignore
            print(f"- {doc_score:.4f}  ({doc_position:>3})  {self.documents[doc_position][:100]}...")
        
        return []
