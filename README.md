# 🍽️ Restaurant Recommendation System

A restaurant recommendation engine built from scratch using core data structures
and algorithms — a Trie for name search, a graph with Dijkstra's algorithm for
cuisine-similarity expansion, cosine similarity for scoring, and a max-heap for
ranking. Includes a CLI (`main.py`) and a Streamlit web app (`app.py`).

## Features

- **Trie** — fast prefix search over restaurant names, powers name autocomplete
- **Graph + Dijkstra** — restaurants are connected by shared cuisines (edge
  weight = `1 - Jaccard similarity`); Dijkstra expands a seed match into a
  pool of nearby, cuisine-similar candidates
- **Cosine similarity** — scores each candidate against a user preference
  vector `[spice_level, veg_friendly, price_normalized, rating_normalized]`
- **Max-Heap** — extracts the top 5 highest-scoring restaurants
- **Merge sort** — recursive sort utility for ranking by any key
- Streamlit UI with sidebar filters, name autocomplete, styled result cards,
  and a NetworkX visualization of the candidate similarity graph

## Project Structure

```
.
├── app.py                 # Streamlit web app
├── main.py                # CLI entry point
├── conftest.py             # pytest path setup
├── requirements.txt
├── data/
│   └── restaurants.json   # 60 sample restaurants
├── modules/
│   ├── trie.py             # Trie / TrieNode
│   ├── graph.py             # RestaurantGraph (adjacency list)
│   ├── traversal.py         # bfs, dijkstra
│   ├── scorer.py             # cosine_similarity, score_restaurants
│   └── ranker.py             # MaxHeap, get_top_k, merge_sort
└── tests/
    └── test_all.py         # pytest suite for all modules
```

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

## Running the CLI

```bash
python main.py
```

You'll be prompted for a preferred cuisine, max price, and minimum rating,
then shown a ranked table of the top 5 matches.

## Running the Streamlit App

```bash
streamlit run app.py
```

Use the sidebar to set cuisine, price, and rating filters, search by name at
the top, and click **Get Recommendations** to see ranked result cards and the
similarity graph.

## Running Tests

```bash
pytest tests/test_all.py
```

> Note: if you have the `langsmith` package installed, its pytest plugin can
> crash on collection in some environments. If tests fail to even start,
> run with plugin autoloading disabled:
> ```bash
> PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/test_all.py   # macOS/Linux
> set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 && pytest tests/test_all.py   # Windows cmd
> ```

## Tech Stack

- Python 3.12
- Streamlit — web UI
- NetworkX + Matplotlib — graph visualization
- pytest — testing
