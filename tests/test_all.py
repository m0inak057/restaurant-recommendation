import math

from modules.trie import Trie
from modules.graph import RestaurantGraph
from modules.scorer import cosine_similarity
from modules.ranker import MaxHeap, merge_sort


# ---------------------------------------------------------------------------
# Trie
# ---------------------------------------------------------------------------

def test_trie_insert_and_prefix_search():
    trie = Trie()
    trie.insert("Tandoori Nights", "R001")
    trie.insert("Tandoor Express", "R002")
    trie.insert("Curry Leaf", "R003")

    results = trie.search_prefix("Tando")
    assert set(results) == {"R001", "R002"}


def test_trie_prefix_search_no_match():
    trie = Trie()
    trie.insert("Curry Leaf", "R003")

    assert trie.search_prefix("Pizza") == []


def test_trie_empty_string_prefix():
    trie = Trie()
    trie.insert("Curry Leaf", "R003")

    # An empty prefix never descends into any child node, so nothing is
    # collected (ids are only stored on nodes reached by consuming a
    # character), giving an empty result rather than "all restaurants".
    assert trie.search_prefix("") == []


def test_trie_case_insensitivity():
    trie = Trie()
    trie.insert("Curry Leaf", "R003")

    assert trie.search_prefix("curry") == ["R003"]
    assert trie.search_prefix("CURRY") == ["R003"]
    assert trie.search_prefix("CuRrY") == ["R003"]


# ---------------------------------------------------------------------------
# RestaurantGraph
# ---------------------------------------------------------------------------

def test_graph_add_node():
    graph = RestaurantGraph()
    graph.add_node("R001")

    assert "R001" in graph.get_all_nodes()


def test_graph_add_edge_and_neighbors():
    graph = RestaurantGraph()
    graph.add_edge("R001", "R002", 0.8)

    neighbors_r1 = graph.get_neighbors("R001")
    neighbors_r2 = graph.get_neighbors("R002")

    assert neighbors_r1 == {"R002": 0.8}
    assert neighbors_r2 == {"R001": 0.8}


def test_graph_get_all_nodes():
    graph = RestaurantGraph()
    graph.add_edge("R001", "R002", 0.5)
    graph.add_node("R003")

    assert set(graph.get_all_nodes()) == {"R001", "R002", "R003"}


def test_graph_get_neighbors_of_unknown_node():
    graph = RestaurantGraph()

    assert graph.get_neighbors("R999") == {}


# ---------------------------------------------------------------------------
# cosine_similarity
# ---------------------------------------------------------------------------

def test_cosine_similarity_identical_vectors():
    vec = [0.8, 0.5, 0.3, 0.9]

    assert math.isclose(cosine_similarity(vec, vec), 1.0, rel_tol=1e-9)


def test_cosine_similarity_orthogonal_vectors():
    vec_a = [1.0, 0.0]
    vec_b = [0.0, 1.0]

    assert math.isclose(cosine_similarity(vec_a, vec_b), 0.0, abs_tol=1e-9)


def test_cosine_similarity_zero_vector():
    vec_a = [0.0, 0.0, 0.0]
    vec_b = [0.5, 0.5, 0.5]

    assert cosine_similarity(vec_a, vec_b) == 0.0


# ---------------------------------------------------------------------------
# MaxHeap
# ---------------------------------------------------------------------------

def test_max_heap_extract_max_returns_highest_score():
    heap = MaxHeap()
    heap.insert(0.5, "R001")
    heap.insert(0.9, "R002")
    heap.insert(0.2, "R003")

    score, item = heap.extract_max()
    assert score == 0.9
    assert item == "R002"


def test_max_heap_extracts_in_descending_order():
    heap = MaxHeap()
    for score, item in [(0.3, "R001"), (0.9, "R002"), (0.6, "R003"), (0.1, "R004")]:
        heap.insert(score, item)

    extracted_scores = [heap.extract_max()[0] for _ in range(4)]
    assert extracted_scores == sorted(extracted_scores, reverse=True)


def test_max_heap_size_and_peek():
    heap = MaxHeap()
    assert heap.size() == 0

    heap.insert(0.4, "R001")
    heap.insert(0.7, "R002")

    assert heap.size() == 2
    assert heap.peek() == (0.7, "R002")
    # peek should not remove the item
    assert heap.size() == 2


# ---------------------------------------------------------------------------
# merge_sort
# ---------------------------------------------------------------------------

def test_merge_sort_sorts_dicts_by_key_descending():
    restaurants = [
        {"id": "R001", "similarity_score": 0.4},
        {"id": "R002", "similarity_score": 0.9},
        {"id": "R003", "similarity_score": 0.1},
        {"id": "R004", "similarity_score": 0.6},
    ]

    sorted_restaurants = merge_sort(restaurants, "similarity_score")

    assert [r["id"] for r in sorted_restaurants] == ["R002", "R004", "R001", "R003"]


def test_merge_sort_empty_and_single_element():
    assert merge_sort([], "similarity_score") == []

    single = [{"id": "R001", "similarity_score": 0.5}]
    assert merge_sort(single, "similarity_score") == single


def test_merge_sort_does_not_mutate_input():
    restaurants = [
        {"id": "R001", "similarity_score": 0.2},
        {"id": "R002", "similarity_score": 0.8},
    ]
    original_order = [r["id"] for r in restaurants]

    merge_sort(restaurants, "similarity_score")

    assert [r["id"] for r in restaurants] == original_order
