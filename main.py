import json
import os

from modules.trie import Trie
from modules.graph import RestaurantGraph
from modules.traversal import dijkstra
from modules.scorer import cosine_similarity
from modules.ranker import get_top_k

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "restaurants.json")

# Hardcoded user preference vector: [spice_level, veg_friendly,
# price_normalized, rating_normalized]. Weighted toward spicy, mildly
# veg-friendly, budget-conscious, highly-rated places.
USER_VECTOR = [0.8, 0.5, 0.3, 0.9]

# How close (by shared-cuisine distance) a restaurant must be to a matched
# seed restaurant to be pulled into the expanded candidate pool.
DIJKSTRA_DISTANCE_THRESHOLD = 0.9

TOP_K = 5


def load_restaurants(path):
    """Load restaurants.json into a HashMap (dict) keyed by restaurant id."""
    with open(path, "r", encoding="utf-8") as f:
        restaurant_list = json.load(f)
    return {r["id"]: r for r in restaurant_list}


def build_trie(restaurant_map):
    """Build a Trie over every restaurant name, mapping name -> id."""
    trie = Trie()
    for restaurant_id, restaurant in restaurant_map.items():
        trie.insert(restaurant["name"], restaurant_id)
    return trie


def jaccard_similarity(set_a, set_b):
    """Similarity of two cuisine sets: |intersection| / |union|."""
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union)


def build_graph(restaurant_map):
    """
    Build a RestaurantGraph connecting any two restaurants that share at
    least one cuisine. Edge weight is stored as a distance
    (1 - jaccard similarity of their cuisine sets), so more similar
    restaurants are "closer" together for Dijkstra's shortest-path search.
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
                distance = 1.0 - similarity
                graph.add_edge(id_a, id_b, distance)

    return graph


def prompt_user():
    """Ask the CLI user for preferred cuisine, max price, and min rating."""
    cuisine = input("Preferred cuisine (e.g. Indian, Chinese, Italian): ").strip()
    max_price_raw = input("Max price for two (INR): ").strip()
    min_rating_raw = input("Minimum rating (0.0 - 5.0): ").strip()

    max_price = float(max_price_raw) if max_price_raw else float("inf")
    min_rating = float(min_rating_raw) if min_rating_raw else 0.0

    return cuisine, max_price, min_rating


def find_seed_matches(trie, restaurant_map, cuisine):
    """
    Find candidate restaurant IDs matching the user's cuisine preference:
    restaurants whose name starts with the typed text (via the Trie), plus
    restaurants whose cuisine list actually contains the preference.
    """
    seeds = set(trie.search_prefix(cuisine))

    cuisine_lower = cuisine.lower()
    for restaurant_id, restaurant in restaurant_map.items():
        if any(c.lower() == cuisine_lower for c in restaurant["cuisine"]):
            seeds.add(restaurant_id)

    return seeds


def expand_candidates(graph, seed_ids):
    """
    Use Dijkstra's algorithm from each seed restaurant to expand the
    candidate pool with nearby (cuisine-similar) restaurants, keeping
    those within DIJKSTRA_DISTANCE_THRESHOLD.
    """
    candidates = set(seed_ids)

    for seed_id in seed_ids:
        distances = dijkstra(graph, seed_id)
        for restaurant_id, distance in distances.items():
            if distance <= DIJKSTRA_DISTANCE_THRESHOLD:
                candidates.add(restaurant_id)

    return candidates


def filter_candidates(restaurant_map, candidate_ids, max_price, min_rating):
    """Keep only candidates within the user's price and rating constraints."""
    filtered = []
    for restaurant_id in candidate_ids:
        restaurant = restaurant_map[restaurant_id]
        if restaurant["price_for_two"] <= max_price and restaurant["rating"] >= min_rating:
            filtered.append(restaurant)
    return filtered


def score_candidates(candidates):
    """Score each candidate restaurant against USER_VECTOR via cosine similarity."""
    scored = []
    for restaurant in candidates:
        score = cosine_similarity(USER_VECTOR, restaurant["feature_vector"])
        scored.append({**restaurant, "similarity_score": score})
    return scored


def print_results(results):
    """Print the top results as a clean formatted table."""
    if not results:
        print("\nNo restaurants matched your preferences.")
        return

    header = f"{'ID':<6}{'Name':<22}{'Cuisine':<20}{'Price':>8}{'Rating':>8}{'Score':>8}"
    print("\n" + header)
    print("-" * len(header))

    for r in results:
        cuisine_str = ", ".join(r["cuisine"])
        print(
            f"{r['id']:<6}{r['name']:<22}{cuisine_str:<20}"
            f"{r['price_for_two']:>8}{r['rating']:>8.1f}{r['similarity_score']:>8.3f}"
        )


def main():
    restaurant_map = load_restaurants(DATA_PATH)
    trie = build_trie(restaurant_map)
    graph = build_graph(restaurant_map)

    cuisine, max_price, min_rating = prompt_user()

    seed_ids = find_seed_matches(trie, restaurant_map, cuisine)
    if not seed_ids:
        print(f"\nNo restaurants found matching '{cuisine}'.")
        return

    candidate_ids = expand_candidates(graph, seed_ids)
    candidates = filter_candidates(restaurant_map, candidate_ids, max_price, min_rating)

    if not candidates:
        print("\nNo restaurants matched your price/rating constraints.")
        return

    scored = score_candidates(candidates)
    top_results = get_top_k(scored, TOP_K)

    print_results(top_results)


if __name__ == "__main__":
    main()
