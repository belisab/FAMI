from sklearn.feature_extraction.text import CountVectorizer
from bs4 import BeautifulSoup
from pathlib import Path
import nltk
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# Operators and/AND, or/OR, not/NOT become &, |, 1 -
# Parentheses are left untouched
# Everything else is interpreted as a term and fed
# through td_matrix[t2i["..."]]
d = {"and": "&", "AND": "&",
     "or": "|", "OR": "|",
     "not": "1 -", "NOT": "1 -",
     "(": "(", ")": ")"}  # operator replacements

# define documents
p = Path(__file__).with_name('documents.txt')
with p.open(encoding="utf-8") as f:
    document = f.read()

soup = BeautifulSoup(document, 'html.parser')
articles = soup.find_all('article')

documents = []
for article in articles:
    documents.append(str(article))


# rewrite tokens
def rewrite_token(t, td_matrix, t2i):
    # returns t d_matrix[t2i["is"]]
    return d.get(t, 'td_matrix[t2i["{:s}"]]'.format(t))


def rewrite_query(query, td_matrix, t2i):
    # rewrite every token in the query
    return " ".join(rewrite_token(t, td_matrix, t2i) for t in query.split())


def test_query(query, td_matrix, t2i, documents):
    print("Query: '" + query + "'")
    print("Rewritten:", rewrite_query(query, td_matrix, t2i))
    # Eval runs the string as a Python command
    print("Matching:", eval(rewrite_query(query, td_matrix, t2i)))
    # finding the matching document
    hits_matrix = eval(rewrite_query(query, td_matrix, t2i))
    hits_list = list(hits_matrix.nonzero()[1])
    # prints the first 500 characters of the matching document
    for i, doc_idx in enumerate(hits_list):
        print("Matching doc #{:d}: {:s}".format(i, (documents[doc_idx][:500])))


def create_tf_matrix():
    # sublinear_tf = True create logarithmic term frequencies
    # use_idf = True shows inversed document frequencies indicating rarity
    # norm=l2 normalises all document vectors (columns) to have a (Euclidian)
    # length of one:
    tf = TfidfVectorizer(lowercase=True, sublinear_tf=True, use_idf=True,
                           norm="l2")
    tf_matrix = tf.fit_transform(documents).T.todense()
    return tf_matrix


def test_tf_idf_query(query, tf_matrix, t2i):
    print("Query: '" + query + "'")
    print("Rewritten:", rewrite_query(query, tf_matrix, t2i))

    hits_list4 = np.array(tf_matrix[t2i[query]])[0]
    hits_and_doc_ids = [(hits, i) for i, hits in enumerate(hits_list4) if
                        hits > 0]
    ranked_hits_and_doc_ids = sorted(hits_and_doc_ids, reverse=True)

    print("\nMatched the following documents, ranked highest relevance first:")
    for hits, i in ranked_hits_and_doc_ids:
        print(
            "Score of 'example' is {:.4f} in document: {:s}".format(hits,
            documents[i][:500]))

def main():
    cv = CountVectorizer(lowercase=True, binary=False)
    dense_matrix = cv.fit_transform(documents).T.todense()

    sparse_matrix = cv.fit_transform(documents)
    # print("Term-document matrix: (?)\n")
    # print(sparse_matrix)


    #print("Term-document matrix: (?)\n")
    #print(dense_matrix)

    td_matrix = dense_matrix.T  # .T transposes the matrix

    #print("Term-document matrix:\n")
    #print(td_matrix)

    t2i = cv.vocabulary_
    #print(t2i)

    while True:
        query = input("Search for something. If you want to stop your search "
                      "type 'q'. Search: ")
        query = query.lower()

        if query == "q":
            break
        else:
            print(query)
            # because td_matrix and t2i are defined in main(), also pass these
            # to other functions
            test_query(query, td_matrix, t2i, documents)

    # -- tf-idf --

    tf_matrix = create_tf_matrix()
    test_tf_idf_query("candy", tf_matrix, t2i)




main()