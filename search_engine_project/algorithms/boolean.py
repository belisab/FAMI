
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

    starts_with_star = pattern.startswith("*")
    ends_with_star = pattern.endswith("*")

    for i, part in enumerate(parts):
        if not part:
            continue

        segment = part
        if i == 0 and not starts_with_star:
            segment = "$" + segment
        if i == len(parts) - 1 and not ends_with_star:
            segment = segment + "$"

        if len(segment) < k:
            continue

        for j in range(len(segment) - k + 1):
            kgrams.append(segment[j:j+k])

    return kgrams

# Expand wildcard pattern using k-gram index
def expand_wildcard(pattern: str, kgram_index: KGramIndex, vocabulary) -> list[str]:
    vocab_list = list(vocabulary)

    kgrams = kgrams_from_wildcard(pattern)
    if not kgrams:
        return [t for t in vocab_list if fnmatch.fnmatch(t, pattern)]

    candidates: set[str] | None = None

    for kg in kgrams:
        bucket = kgram_index.get(kg)
        if not bucket:
            return [t for t in vocab_list if fnmatch.fnmatch(t, pattern)]

        candidates = bucket.copy() if candidates is None else (candidates & bucket)

    if not candidates:
        return [t for t in vocab_list if fnmatch.fnmatch(t, pattern)]

    return [t for t in candidates if fnmatch.fnmatch(t, pattern)]

# Expand wildcards in the entire query
def expand_wildcards_in_tokens(tokens: 'list[Token]', kgram_index: KGramIndex, vocabulary) -> 'list[Token]':
    out: list[Token] = []

    for tk in tokens:
        if (not tk.kw) and ("*" in tk.value):
            expanded = expand_wildcard(tk.value, kgram_index, vocabulary)

            if expanded:
                out.append(Token(True, "("))
                for i, term in enumerate(expanded):
                    if i > 0:
                        out.append(Token(True, "|"))
                    out.append(Token(False, term))
                out.append(Token(True, ")"))
            else:
                out.append(Token(False, "__nomatch__"))
        else:
            out.append(tk)

    return out

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

    while True:
        tk = tokens.peek(None)
        if tk is None:
            break
        if tk.kw and tk.value in {")", "|", "&"}:
            break

        more = parse_binop_stmt(tokens)
        if not more:
            break

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

        tokens = tokenize_query(query)

        if self.kgram_index:
            tokens = expand_wildcards_in_tokens(
                tokens,
                self.kgram_index,
                self.data["t2i"].keys()
            )

        ast = parse_stmt(peekable(tokens))
        if ast is None:
            return []

        hits_matrix = ast.eval(self.data)
        hits_list = list(hits_matrix.nonzero()[1])

        return [self.documents[doc_idx] for doc_idx in hits_list]
