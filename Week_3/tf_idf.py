from sklearn.feature_extraction.text import CountVectorizer
from bs4 import BeautifulSoup
from pathlib import Path
#import nltk
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

# Rewrite boolean query
def rewrite_query(query, td_matrix, t2i, tokenizer):
    # rewrite every token in the query
    # using a tokenizer instead of query.split

    return " & ".join(
        rewrite_token(t, td_matrix, t2i)
        for t in tokenizer(query)
        if t not in ("and", "or", "not")
    )


def boolean_query(query, td_matrix, t2i, documents, tokenizer):
    print("Query: '" + query + "'")
    tokens = tokenizer(query)
    print("Rewritten:", rewrite_query(query, td_matrix, t2i, tokenizer))
    # Eval runs the string as a Python command
    print("Matching:", eval(rewrite_query(query, td_matrix, t2i, tokenizer)))
    # finding the matching document
    hits_matrix = eval(rewrite_query(query, td_matrix, t2i, tokenizer))
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


def test_tf_idf_query(query, tf_matrix, t2i, cv, tokenizer):
    print("Query: '" + query + "'")
    print("Rewritten:", rewrite_query(query, tf_matrix, t2i, tokenizer))

    tokens = tokenizer(query)
    hits = np.zeros(tf_matrix.shape[1])

    for t in tokens:
        if t in t2i:
            hits += np.array(tf_matrix[t2i[t]])[0]
    hits_list4 = hits
    hits_and_doc_ids = [(hits, i) for i, hits in enumerate(hits_list4) if
                        hits > 0]
    ranked_hits_and_doc_ids = sorted(hits_and_doc_ids, reverse=True)

    print("\nMatched the following documents, ranked highest relevance first:")
    for hits, i in ranked_hits_and_doc_ids:
        print(
            "Score of 'example' is {:.4f} in document: {:s}".format(hits,
            documents[i][:500]))

def main():
<<<<<<< HEAD
    # cv for boolean search
    cv1 = CountVectorizer(lowercase=True, binary=True)
    # cv for tf-idf
    cv2 = CountVectorizer(lowercase=True, binary=False)
    cv2.fit(documents)
    x = cv1.fit_transform(documents)
    dense_matrix = x.todense()

    sparse_matrix = x
=======
    cv1 = CountVectorizer(lowercase=True, binary=True)

    sparse_matrix = cv1.fit_transform(documents)
    dense_matrix = sparse_matrix.todense()
>>>>>>> 4694367cc0b7e8f348c12391fa2d66cb883f70b0
    # print("Term-document matrix: (?)\n")
    # print(sparse_matrix)


    #print("Term-document matrix: (?)\n")
    #print(dense_matrix)

    td_matrix = dense_matrix.T # .T transposes the matrix

    tf_matrix = create_tf_matrix()

    #print("Term-document matrix:\n")
    #print(td_matrix)

    t2i = cv1.vocabulary_
<<<<<<< HEAD
    t2i2 = cv2.vocabulary_
    
=======
>>>>>>> 4694367cc0b7e8f348c12391fa2d66cb883f70b0
    #print(t2i)
    
    tokenizer1 = cv1.build_tokenizer()
    tokenizer2 = cv2.build_tokenizer()


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
            print("\n Boolean search results: \n")
            boolean_query(query, td_matrix, t2i, documents, tokenizer1)
            print("\n TF-IDF search results: \n")
            test_tf_idf_query(query, tf_matrix, t2i2, cv2, tokenizer2)

    # -- tf-idf --
   
    
    

<<<<<<< HEAD
    #test_tf_idf_query("candy", tf_matrix, t2iv2)


=======
    cv2 = CountVectorizer(lowercase=True, binary=False)
    t2iv2 = cv2.vocabulary_

    tf_matrix = create_tf_matrix()
    test_tf_idf_query("candy", tf_matrix, t2iv2)
>>>>>>> 4694367cc0b7e8f348c12391fa2d66cb883f70b0


main()