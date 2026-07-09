import math


def cosine_similarity(vec_a, vec_b):
    """
    Compute the cosine similarity between two equal-length vectors of
    floats, returning a value between 0.0 and 1.0 (assuming non-negative
    feature vectors, as used for restaurant feature vectors in this
    project). Returns 0.0 if either vector is a zero-vector, since cosine
    similarity is undefined when a magnitude is zero.

    Time complexity: O(n) where n is the vector length.
    """
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))

    magnitude_a = math.sqrt(sum(a * a for a in vec_a))
    magnitude_b = math.sqrt(sum(b * b for b in vec_b))

    if magnitude_a == 0.0 or magnitude_b == 0.0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def score_restaurants(user_vector, restaurant_list):
    """
    Score each restaurant in restaurant_list by cosine similarity between
    user_vector and the restaurant's "feature_vector", returning a new list
    of restaurant dicts (each augmented with a "similarity_score" key)
    sorted by similarity score descending.

    Time complexity: O(n * d) to score all n restaurants (each of vector
    length d), plus O(n log n) to sort by score.
    """
    scored = []
    for restaurant in restaurant_list:
        score = cosine_similarity(user_vector, restaurant["feature_vector"])
        scored_restaurant = {**restaurant, "similarity_score": score}
        scored.append(scored_restaurant)

    scored.sort(key=lambda r: r["similarity_score"], reverse=True)
    return scored
