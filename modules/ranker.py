import heapq


class MaxHeap:
    def __init__(self):
        """
        Initialize an empty max-heap backed by heapq (a min-heap), storing
        (-score, insertion_order, item) tuples so the largest score is
        always at the root. insertion_order breaks ties so items are never
        compared directly.

        Time complexity: O(1)
        """
        self.heap = []
        self._counter = 0

    def insert(self, score, item):
        """
        Insert an item with the given score into the heap.

        Time complexity: O(log n) where n is the number of items in the heap.
        """
        heapq.heappush(self.heap, (-score, self._counter, item))
        self._counter += 1

    def extract_max(self):
        """
        Remove and return the (score, item) pair with the highest score.

        Time complexity: O(log n) where n is the number of items in the heap.
        """
        if not self.heap:
            return None
        neg_score, _, item = heapq.heappop(self.heap)
        return (-neg_score, item)

    def peek(self):
        """
        Return the (score, item) pair with the highest score without
        removing it.

        Time complexity: O(1)
        """
        if not self.heap:
            return None
        neg_score, _, item = self.heap[0]
        return (-neg_score, item)

    def size(self):
        """
        Return the number of items currently in the heap.

        Time complexity: O(1)
        """
        return len(self.heap)


def get_top_k(scored_restaurants, k):
    """
    Insert all restaurants into a MaxHeap keyed by "similarity_score" and
    extract the top k restaurant dicts, highest score first.

    Time complexity: O(n log n) — n inserts plus up to n extracts, each
    O(log n), where n is the number of restaurants.
    """
    heap = MaxHeap()
    for restaurant in scored_restaurants:
        heap.insert(restaurant["similarity_score"], restaurant)

    top_k = []
    for _ in range(min(k, heap.size())):
        _, item = heap.extract_max()
        top_k.append(item)

    return top_k


def merge_sort(restaurant_list, key):
    """
    Recursively sort a list of restaurant dicts in descending order by the
    given key using merge sort.

    Time complexity: O(n log n) where n is the length of restaurant_list.
    """
    if len(restaurant_list) <= 1:
        return list(restaurant_list)

    mid = len(restaurant_list) // 2
    left = merge_sort(restaurant_list[:mid], key)
    right = merge_sort(restaurant_list[mid:], key)

    return _merge(left, right, key)


def _merge(left, right, key):
    """
    Merge two lists, each already sorted descending by key, into a single
    sorted-descending list.

    Time complexity: O(n) where n is the combined length of left and right.
    """
    merged = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i][key] >= right[j][key]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged
