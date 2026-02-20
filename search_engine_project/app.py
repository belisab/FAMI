from flask import Flask, render_template, request
from data_loader import load_documents
from visualisations import years_bar
from visualisations import venue_pie

app = Flask(__name__)

from algorithms.boolean import BooleanSearchEngine
from algorithms.semantic import SemanticSearchEngine

documents = load_documents()
boolean_engine = BooleanSearchEngine(documents)

_semantic_engine = None  # lazy

def get_semantic_engine():
    global _semantic_engine
    if _semantic_engine is None:
        ft_model = SemanticSearchEngine.install_embeddings()
        _semantic_engine = SemanticSearchEngine(ft_model, documents)
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

    MAX_RESULTS = 10 # Limit the number of results to display

    if method == "boolean":
        hits = boolean_engine.search(query)
    elif method == "semantic":
        hits = get_semantic_engine().search(query)
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
