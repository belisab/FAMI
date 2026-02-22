from flask import Flask, render_template, request
from data_loader import load_documents
from visualisations import years_bar
from visualisations import venue_pie

import threading

app = Flask(__name__)

from algorithms.boolean import BooleanSearchEngine
from algorithms.semantic import SemanticSearchEngine

documents = load_documents()
boolean_engine = BooleanSearchEngine(documents)
semantic_engine: SemanticSearchEngine | None = None

# Thread safety my beloved :3
semantic_engine_lock = threading.Lock()

def load_semantic_engine():
    global semantic_engine
    print("Downloading dataset, this will take a while")
    ft_model = SemanticSearchEngine.install_embeddings()
    print("Loading dataset")
    se = SemanticSearchEngine(ft_model, documents)
    print("Dataset loaded")

    # Avoid holding the lock for too long
    with semantic_engine_lock:
        semantic_engine = se

semantic_load_thread = threading.Thread(target=load_semantic_engine)

@app.route("/")
def home():
    return render_template("ui.html")

@app.route("/search")
def search():
    with semantic_engine_lock:
        if not semantic_engine and not semantic_load_thread.is_alive():
            semantic_load_thread.start()
        return render_template("search.html", semantic_engine_loaded=semantic_engine is not None)

@app.route("/semantic-engine-status")
def semantic_engine_status():
    with semantic_engine_lock:
        return { "semantic-engine-loaded": semantic_engine is not None }

@app.route("/results")
def results():
    query = request.args.get("query", "")
    method = request.args.get("method", "boolean")

    MAX_RESULTS = 20 # Limit the number of results to display

    if method == "boolean":
        hits = boolean_engine.search(query)
    elif method == "semantic":
        with semantic_engine_lock:
            if semantic_engine is None:
                return "Semantic search engine has not yet been loaded", 500
            hits = semantic_engine.search(query)
    else:
        hits = []

    # for visualisations
    # extract years
    years = [int(hit.year_released[:4]) for hit in hits if hit.year_released[:4]]
    # generate plot by referencing visualisations.py
    plot_file = years_bar(years) if years else None

    venues = [hit.venue_type for hit in hits if hit.venue_type]
    pie_plot = venue_pie(venues) if venues else None

    hits = hits[:MAX_RESULTS]  # Limit results to MAX_RESULTS

    # return plots
    return render_template("results.html", query=query, method=method,
                           results=hits, plot_file=plot_file,
                           pie_plot=pie_plot)

@app.route("/results/<index>")
def musical(index: str):
    return render_template("musical.html", musical=documents[int(index)])

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
