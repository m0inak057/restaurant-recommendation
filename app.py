import json
import os

import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

from modules.trie import Trie
from modules.graph import RestaurantGraph
from modules.traversal import dijkstra
from modules.scorer import cosine_similarity
from modules.ranker import get_top_k

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "restaurants.json")

# Hardcoded user preference vector: [spice_level, veg_friendly,
# price_normalized, rating_normalized].
USER_VECTOR = [0.8, 0.5, 0.3, 0.9]

DIJKSTRA_DISTANCE_THRESHOLD = 0.9
TOP_K = 5


@st.cache_data
def load_restaurants(path):
    """Load restaurants.json into a HashMap (dict) keyed by restaurant id."""
    with open(path, "r", encoding="utf-8") as f:
        restaurant_list = json.load(f)
    return {r["id"]: r for r in restaurant_list}


@st.cache_resource
def build_trie(restaurant_map):
    """Build a Trie over every restaurant name, mapping name -> id."""
    trie = Trie()
    for restaurant_id, restaurant in restaurant_map.items():
        trie.insert(restaurant["name"], restaurant_id)
    return trie


def jaccard_similarity(set_a, set_b):
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


@st.cache_resource
def build_graph(restaurant_map):
    """
    Build a RestaurantGraph connecting restaurants that share at least one
    cuisine. Edge weight is stored as a distance (1 - jaccard similarity),
    so more similar restaurants are "closer" for Dijkstra's search.
    """
    graph = RestaurantGraph()
    ids = list(restaurant_map.keys())

    for restaurant_id in ids:
        graph.add_node(restaurant_id)

    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            id_a, id_b = ids[i], ids[j]
            cuisines_a = set(c.lower() for c in restaurant_map[id_a]["cuisine"])
            cuisines_b = set(c.lower() for c in restaurant_map[id_b]["cuisine"])

            if cuisines_a & cuisines_b:
                similarity = jaccard_similarity(cuisines_a, cuisines_b)
                graph.add_edge(id_a, id_b, 1.0 - similarity)

    return graph


def find_seed_matches(trie, restaurant_map, search_query, cuisine):
    """
    Candidate restaurant IDs from the search bar's Trie prefix match, plus
    restaurants whose cuisine list contains the sidebar cuisine selection.
    """
    seeds = set()

    if search_query:
        seeds.update(trie.search_prefix(search_query))

    cuisine_lower = cuisine.lower()
    for restaurant_id, restaurant in restaurant_map.items():
        if any(c.lower() == cuisine_lower for c in restaurant["cuisine"]):
            seeds.add(restaurant_id)

    return seeds


def expand_candidates(graph, seed_ids):
    """Use Dijkstra from each seed to pull in nearby, cuisine-similar restaurants."""
    candidates = set(seed_ids)
    for seed_id in seed_ids:
        distances = dijkstra(graph, seed_id)
        for restaurant_id, distance in distances.items():
            if distance <= DIJKSTRA_DISTANCE_THRESHOLD:
                candidates.add(restaurant_id)
    return candidates


def filter_candidates(restaurant_map, candidate_ids, max_price, min_rating):
    filtered = []
    for restaurant_id in candidate_ids:
        restaurant = restaurant_map[restaurant_id]
        if restaurant["price_for_two"] <= max_price and restaurant["rating"] >= min_rating:
            filtered.append(restaurant)
    return filtered


def score_candidates(candidates):
    scored = []
    for restaurant in candidates:
        score = cosine_similarity(USER_VECTOR, restaurant["feature_vector"])
        scored.append({**restaurant, "similarity_score": score})
    return scored


def render_similarity_graph(graph, subgraph_ids, highlighted_ids, restaurant_map, seed_count):
    """
    Draw the restaurant similarity graph (restricted to subgraph_ids, the
    candidate pool considered for this search) using NetworkX, with the
    top results highlighted in a different color.
    """
    st.markdown(
        """
        🔴 **Red nodes** = Top 5 recommended restaurants (highlighted)
        &nbsp;&nbsp;|&nbsp;&nbsp;
        🔵 **Blue nodes** = Other candidates considered but not in top 5
        &nbsp;&nbsp;|&nbsp;&nbsp;
        **Lines** = shared cuisine connection (edge weight = Jaccard distance)
        """
    )

    nx_graph = nx.Graph()
    subgraph_set = set(subgraph_ids)

    for restaurant_id in subgraph_ids:
        nx_graph.add_node(restaurant_id)

    for restaurant_id in subgraph_ids:
        for neighbor_id, weight in graph.get_neighbors(restaurant_id).items():
            if neighbor_id in subgraph_set:
                nx_graph.add_edge(restaurant_id, neighbor_id, weight=weight)

    if nx_graph.number_of_nodes() == 0:
        st.info("No graph data to display for this search.")
        return

    background_color = "#1a1a2e"
    red_color = "#ff4b4b"
    blue_color = "#4b8eff"
    edge_color = "#444466"

    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor(background_color)
    ax.set_facecolor(background_color)

    pos = nx.spring_layout(nx_graph, seed=42)

    node_colors = [
        red_color if node_id in highlighted_ids else blue_color
        for node_id in nx_graph.nodes()
    ]
    node_sizes = [
        700 if node_id in highlighted_ids else 300
        for node_id in nx_graph.nodes()
    ]

    blue_nodes = [n for n in nx_graph.nodes() if n not in highlighted_ids]
    if nx_graph.number_of_nodes() > 20:
        # Too many nodes to label legibly: label the red (top 5) nodes plus
        # only the 5 highest-degree blue nodes.
        blue_label_nodes = set(
            sorted(blue_nodes, key=lambda n: nx_graph.degree(n), reverse=True)[:5]
        )
    else:
        blue_label_nodes = set(blue_nodes)

    red_labels = {
        node_id: restaurant_map[node_id]["name"]
        for node_id in nx_graph.nodes()
        if node_id in highlighted_ids
    }
    blue_labels = {
        node_id: restaurant_map[node_id]["name"]
        for node_id in blue_label_nodes
    }

    nx.draw_networkx_edges(nx_graph, pos, ax=ax, alpha=0.4, edge_color=edge_color)
    nx.draw_networkx_nodes(
        nx_graph, pos, ax=ax, node_color=node_colors, node_size=node_sizes
    )

    # Offset labels above their node and give them a solid background box so
    # they stay legible regardless of the node color or crossing edge lines.
    label_pos = {node_id: (x, y + 0.06) for node_id, (x, y) in pos.items()}
    label_bbox = dict(boxstyle="round,pad=0.15", facecolor=background_color, edgecolor="none", alpha=0.85)

    nx.draw_networkx_labels(
        nx_graph, label_pos, labels=red_labels, ax=ax, font_size=9,
        font_weight="bold", font_color="#ffffff", bbox=label_bbox,
    )
    nx.draw_networkx_labels(
        nx_graph, label_pos, labels=blue_labels, ax=ax, font_size=7,
        font_color="#ffd166", bbox=label_bbox,
    )

    ax.set_title("Restaurant Similarity Graph (top results highlighted)", color="white")
    ax.axis("off")
    st.pyplot(fig)

    st.caption(
        f"Graph shows {len(subgraph_ids)} restaurants considered. "
        f"Dijkstra's algorithm expanded from {seed_count} seed matches "
        "to build this candidate pool."
    )


CUISINE_BORDER_COLORS = {
    "indian": "#f97316",
    "chinese": "#ef4444",
    "italian": "#22c55e",
    "mexican": "#eab308",
    "continental": "#3b82f6",
    "fast food": "#a855f7",
}


def render_result_card(restaurant):
    primary_cuisine = restaurant["cuisine"][0] if restaurant["cuisine"] else ""
    border_color = CUISINE_BORDER_COLORS.get(primary_cuisine.lower(), "#9ca3af")

    cuisine_badges = "".join(
        f'<span style="display:inline-block; background:#f1f5f9; color:#334155; '
        f'border-radius:999px; padding:2px 10px; margin:2px 4px 2px 0; '
        f'font-size:12px; font-weight:600;">{c}</span>'
        for c in restaurant["cuisine"]
    )

    full_stars = int(round(restaurant["rating"]))
    star_display = "⭐" * max(full_stars, 1)

    match_pct = min(max(restaurant["similarity_score"], 0.0), 1.0) * 100

    with st.container(border=True):
        st.markdown(
            f"""
            <div style="border-left: 6px solid {border_color}; padding: 4px 14px;">
                <div style="font-size:20px; font-weight:700; margin-bottom:4px;">
                    {restaurant['name']}
                </div>
                <div style="margin-bottom:8px;">{cuisine_badges}</div>
                <div style="font-size:14px; color:#475569; margin-bottom:4px;">
                    📍 {restaurant['location']}
                </div>
                <div style="font-size:16px; font-weight:600; margin-bottom:4px;">
                    ₹{restaurant['price_for_two']} for two
                </div>
                <div style="font-size:14px; margin-bottom:6px;">
                    {star_display} {restaurant['rating']:.1f}
                </div>
                <div style="font-size:14px; font-weight:700; color:#16a34a;">
                    {match_pct:.1f}% match
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(min(max(restaurant["similarity_score"], 0.0), 1.0))


def inject_global_style():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #0f0f1a;
            color: #f0f0f0;
        }
        section[data-testid="stSidebar"] {
            background-color: #1a1a2e;
        }
        .block-container {
            padding-top: 1rem;
        }
        .app-header-banner {
            background: linear-gradient(90deg, #1a1a2e, #16213e);
            padding: 24px 28px;
            border-radius: 12px;
            margin-bottom: 24px;
        }
        .app-header-banner h1 {
            color: #ffffff;
            font-size: 34px;
            font-weight: 800;
            margin: 0;
        }
        .app-header-banner p {
            color: #9ca3af;
            font-size: 15px;
            margin: 6px 0 0 0;
        }
        .results-banner {
            background-color: #0d2b1a;
            color: #4ade80;
            padding: 12px 18px;
            border-radius: 8px;
            font-weight: 600;
            margin-bottom: 16px;
        }
        .app-footer {
            text-align: center;
            color: #6b7280;
            font-size: 13px;
            margin-top: 40px;
            padding: 16px 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    st.set_page_config(page_title="Restaurant Recommender", page_icon="🍽️", layout="wide")
    inject_global_style()

    st.markdown(
        """
        <div class="app-header-banner">
            <h1>🍽️ Restaurant Recommendation System</h1>
            <p>Powered by DSA — Trie · Graph · Dijkstra · Cosine Similarity · Max-Heap</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    restaurant_map = load_restaurants(DATA_PATH)
    trie = build_trie(restaurant_map)
    graph = build_graph(restaurant_map)

    all_cuisines = sorted({c for r in restaurant_map.values() for c in r["cuisine"]})

    st.sidebar.markdown("**⚙️ Filter Preferences**")
    cuisine = st.sidebar.selectbox("Cuisine", all_cuisines)
    st.sidebar.divider()
    max_price = st.sidebar.slider("Max price for two (₹)", 100, 2000, 1000, step=50)
    st.sidebar.divider()
    min_rating = st.sidebar.slider("Minimum rating", 3.0, 5.0, 3.5, step=0.1)
    st.sidebar.divider()
    st.sidebar.info("Tip: Use the search bar to narrow by name, and filters to refine by budget and rating.")

    st.markdown("**🔍 Search by restaurant name**")
    search_query = st.text_input("Search restaurants by name", "", label_visibility="collapsed")
    if search_query:
        suggestion_ids = trie.search_prefix(search_query)
        if suggestion_ids:
            suggestion_names = sorted({restaurant_map[rid]["name"] for rid in suggestion_ids})
            st.success("Suggestions: " + ", ".join(suggestion_names[:8]))
        else:
            st.caption("No name matches for that prefix.")

    if st.button("Get Recommendations", type="primary"):
        seed_ids = find_seed_matches(trie, restaurant_map, search_query, cuisine)

        if not seed_ids:
            st.warning("No restaurants matched your search/cuisine.")
            return

        candidate_ids = expand_candidates(graph, seed_ids)
        candidates = filter_candidates(restaurant_map, candidate_ids, max_price, min_rating)

        if not candidates:
            st.warning("No restaurants matched your price/rating constraints.")
            return

        scored = score_candidates(candidates)
        top_results = get_top_k(scored, TOP_K)
        top_ids = {r["id"] for r in top_results}

        st.markdown(
            f"""
            <div class="results-banner">
                ✅ Found {len(candidates)} candidates · Showing Top 5 by similarity score
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.subheader("🏆 Top 5 Recommendations")
        columns = st.columns(len(top_results))
        for col, restaurant in zip(columns, top_results):
            with col:
                render_result_card(restaurant)

        st.divider()

        st.subheader("🕸️ Similarity Graph — How candidates are connected")
        render_similarity_graph(graph, candidate_ids, top_ids, restaurant_map, len(seed_ids))

    st.markdown(
        """
        <div class="app-footer">
            Built with Python · DSA Algorithms · Streamlit | College Project 2026
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
