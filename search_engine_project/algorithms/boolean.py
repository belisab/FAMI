
### This file implements a general Boolean search component that can be imported 
### by later projects without having to rewrite Boolean search again.

from abc import ABC, abstractmethod

from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from scipy import sparse
import typing
from typing import Any, Generic, Sequence, TypeVar, TypedDict
import fnmatch
from algorithms.doc import SearchableDocument
from more_itertools import peekable

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
                new_tokens.append("__EMPTY__")  # no match
        else:
            new_tokens.append(t)

    return " ".join(new_tokens)

class MatrixData(TypedDict):
    td_matrix: Any
    t2i: Any
    empty_row: Any

class Token:
    kw: bool
    value: str

    def __init__(self, kw: bool, value: str) -> None:
        self.kw = kw
        self.value = value

    def is_binop(self) -> bool:
        return self.kw and self.value in "&|"
    
    def unopify(self) -> str:
        match self.value:
            case "&": return "and"
            case "|": return "or"
            case "-": return "not"
            case _: return self.value

OP_CHARS = "&|()-"
OP_WORDS = {
    "and": "&",
    "or":  "|",
    "not": "-",
}

def tokenize_query(query: str) -> list[Token]:
    index = 0
    tokens = list[Token]()
    while index < len(query):
        # Skip spaces
        if query[index].isspace():
            index += 1
            continue
        
        # Collect parenthesized expressions (like "cat and dog")
        if query[index] == '"':
            index += 1
            value = ""
            while index < len(query) and query[index] != '"':
                value += query[index]
                index += 1
            # Consume the last quote as well
            index += 1
            tokens.append(Token(kw=False, value=value))
            continue

        # Operators
        if query[index] in OP_CHARS:
            tokens.append(Token(kw=True, value=query[index]))
            index += 1
            continue

        old_index = index

        # Otherwise, collect a word (text split by spaces or operators)
        word = ""
        while index < len(query) and query[index] not in OP_CHARS and not query[index].isspace():
            word += query[index]
            index += 1
        
        # This should be unreachable, but just in case it isn't, this prevents 
        # the parser from ending up in an infinite loop
        if old_index == index:
            print("ERROR: Boolean query parser did not advance, something is wrong")
            word = query[index]
            index += 1

        # Operators written as words
        if op := OP_WORDS.get(word):
            tokens.append(Token(kw=True, value=op))
            continue

        tokens.append(Token(kw=False, value=word))
    
    return tokens

Matrix = Any

class Stmt(ABC):
    @abstractmethod
    def eval(self, data: MatrixData) -> Matrix:
        pass

class WordStmt(Stmt):
    value: str

    def __init__(self, value: str) -> None:
        super().__init__()
        self.value = value

    def eval(self, data: MatrixData) -> Matrix:
        if self.value in data["t2i"]:
            return data["td_matrix"][data["t2i"][self.value]]
        return data["empty_row"]

class NotStmt(Stmt):
    target: Stmt

    def __init__(self, target: Stmt) -> None:
        super().__init__()
        self.target = target

    def eval(self, data: MatrixData) -> Matrix:
        return 1 - self.target.eval(data)

class BinOpStmt(Stmt):
    lhs: Stmt
    is_and: bool
    rhs: Stmt

    def __init__(self, lhs: Stmt, is_and: bool, rhs: Stmt) -> None:
        super().__init__()
        self.lhs = lhs
        self.is_and = is_and
        self.rhs = rhs

    def eval(self, data: MatrixData) -> Matrix:
        if self.is_and:
            return self.lhs.eval(data) & self.rhs.eval(data)
        return self.lhs.eval(data) | self.rhs.eval(data)

def parse_word_stmt(tokens: 'peekable[Token]') -> Stmt | None:
    cur_token = next(tokens, None)
    if cur_token is None:
        return None
    
    if cur_token.kw:
        if cur_token.value == "(":
            if early_close := tokens.peek(None):
                if early_close.kw and early_close.value == ")":
                    next(tokens)
                    return None
            
            stmt = parse_stmt(tokens)
            # Consume closing parenthesis if provided
            if tk := tokens.peek(None):
                if tk.kw and tk.value == ")":
                    next(tokens)

            return stmt
        
        return WordStmt(cur_token.unopify())
    else:
        return WordStmt(cur_token.value)

def parse_unop_stmt(tokens: 'peekable[Token]') -> Stmt | None:
    # Because you can do double negation like "not not dog"
    unop_count = 0
    while tk := tokens.peek(None):
        if tk.kw and tk.value == "-":
            next(tokens)
            unop_count += 1
        else:
            break
    
    stmt_itself = parse_word_stmt(tokens)
    if stmt_itself is None:
        # If the statement is missing, consider the last "not" to be the word "not" 
        # instead 
        if unop_count > 0:
            stmt_itself = WordStmt("not")
            unop_count -= 1
        else:
            return None

    # An even amount of NOTs results in no NOTs (not not a == a)
    if unop_count % 2 == 0:
        return stmt_itself
    else:
        return NotStmt(stmt_itself)

def parse_binop_stmt(tokens: 'peekable[Token]') -> Stmt | None:
    lhs = parse_unop_stmt(tokens)
    if not lhs:
        return None

    while tk := tokens.peek(None):
        if not tk.is_binop():
            return lhs
        
        # Consume binop
        next(tokens)
        
        # Parse right-hand-side of the operation
        rhs = parse_unop_stmt(tokens)
        if not rhs:
            lhs = BinOpStmt(lhs, True, WordStmt(tk.unopify()))
        else:
            lhs = BinOpStmt(lhs, tk.value == "&", rhs)
    
    return lhs

def parse_stmt(tokens: 'peekable[Token]') -> Stmt | None:
    stmt = parse_binop_stmt(tokens)
    if not stmt:
        return None
    while more := parse_binop_stmt(tokens):
        stmt = BinOpStmt(stmt, True, more)
    return stmt

T = TypeVar('T', bound=SearchableDocument)

class BooleanSearchEngine(Generic[T]):
    documents: Sequence[T]
    data: MatrixData
    kgram_index: KGramIndex | None

    def __init__(self, documents: Sequence[T], support_wildcards: bool = True) -> None:
        self.documents = documents
        cv = CountVectorizer(lowercase=True, binary=True)

        sparse_matrix = typing.cast(
            sparse.spmatrix,
            cv.fit_transform( # type: ignore
                [doc.get_searchable_data() for doc in documents]
            )
        )
        dense_matrix = sparse_matrix.todense()
        td_matrix = dense_matrix.T
        self.data = MatrixData(
            td_matrix=td_matrix,
            t2i=cv.vocabulary_, # type: ignore
            empty_row=np.matrix(np.repeat(0, td_matrix.shape[1]))
        )
        self.kgram_index = build_kgram_index(self.data["t2i"].keys()) if support_wildcards else None

    def search(self, query: str) -> list[T]:
        query = query.lower().strip()
        query = expand_wildcards_in_query(query, self.kgram_index, self.data["t2i"].keys()) if self.kgram_index else query

        # Tokenize query
        tokens = tokenize_query(query)

        ast = parse_stmt(peekable(tokens))
        if ast is None:
            return []
        
        hits_matrix = ast.eval(self.data)
        
        # Finding the matching document
        hits_list = list(hits_matrix.nonzero()[1])

        return [self.documents[doc_idx] for doc_idx in hits_list]
