
from sklearn.feature_extraction.text import CountVectorizer
# Operators and/AND, or/OR, not/NOT become &, |, 1 -
# Parentheses are left untouched
# Everything else is interpreted as a term and fed
# through td_matrix[t2i["..."]]
d = {"and": "&", "AND": "&",
         "or": "|", "OR": "|",
         "not": "1 -", "NOT": "1 -",
         "(": "(", ")": ")"}  # operator replacements

# define toy documents
documents = ["This is a silly example",
             "A better example",
             "Nothing to see here",
             "This is a great and long example"]


def rewrite_token(t, td_matrix, t2i):
    # returns t d_matrix[t2i["is"]]
    return d.get(t, 'td_matrix[t2i["{:s}"]]'.format(t))


def rewrite_query(query, td_matrix, t2i):
    # rewrite every token in the query
    return " ".join(rewrite_token(t, td_matrix, t2i) for t in query.split())


def test_query(query, td_matrix, t2i):
    print("Query: '" + query + "'")
    print("Rewritten:", rewrite_query(query, td_matrix, t2i))
    # Eval runs the string as a Python command
    print("Matching:", eval(rewrite_query(query, td_matrix, t2i)))
    print()


def main():
    cv = CountVectorizer(lowercase=True, binary=True)
    sparse_matrix = cv.fit_transform(documents)

    print("Term-document matrix: (?)\n")
    print(sparse_matrix)

    dense_matrix = sparse_matrix.todense()

    print("Term-document matrix: (?)\n")
    print(dense_matrix)

    td_matrix = dense_matrix.T  # .T transposes the matrix

    print("Term-document matrix:\n")
    print(td_matrix)

    t2i = cv.vocabulary_
    print(t2i)

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
            test_query(query, td_matrix, t2i)

main()