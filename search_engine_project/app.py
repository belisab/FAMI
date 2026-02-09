from flask import Flask, render_template, request
import os, sys
from data_loader import load_documents


app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SEARCH_ALG_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "Search_Algorithms"))
sys.path.insert(0, SEARCH_ALG_DIR)

from boolean import BooleanSearchEngine
from semantic import SemanticSearchEngine

DOCUMENTS, METADATA = load_documents()
boolean_engine = BooleanSearchEngine(DOCUMENTS)


_semantic_engine = None  # lazy

def get_semantic_engine():
    global _semantic_engine
    if _semantic_engine is None:
        ft_model = SemanticSearchEngine.install_embeddings()
        _semantic_engine = SemanticSearchEngine(ft_model, DOCUMENTS)
    return _semantic_engine

@app.route("/")
def home():
    return render_template("ui.html")

@app.route("/search")
def search():
    return render_template("search.html")

@app.route("/results")
def results():
    query = request.args.get("query", "")
    method = request.args.get("method", "boolean")

    MAX_RESULTS = 5 # Limit the number of results to display

    if method == "boolean":
        hits = boolean_engine.search(query)
    elif method == "semantic":
        hits = get_semantic_engine().search(query)
    else:
        hits = []

    hits = hits[:MAX_RESULTS]  # Limit results to MAX_RESULTS

    return render_template("results.html", query=query, method=method, results=hits)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
