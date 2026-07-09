import heapq


def bfs(graph, start_node):
    """
    Breadth-first traversal of a RestaurantGraph starting from start_node.

    Time complexity: O(V + E) where V is the number of nodes and E is the
    number of edges, since each node is visited once and each edge is
    examined once.
    """
    if start_node not in graph.get_all_nodes():
        return []

    visited = {start_node}
    order = []
    # queue holds nodes waiting to be visited, in FIFO order
    queue = [start_node]
    queue_index = 0

    while queue_index < len(queue):
        current = queue[queue_index]
        queue_index += 1
        order.append(current)

        # visit neighbors in insertion order, skipping ones already seen
        for neighbor in graph.get_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return order


def dijkstra(graph, start_node):
    """
    Shortest paths from start_node to every reachable node in a
    RestaurantGraph, using Dijkstra's algorithm with a binary min-heap.
    Edge weights are treated as non-negative costs.

    Time complexity: O((V + E) log V) — each edge relaxation may push a
    new entry onto the heap (O(log V) per push/pop), and every node is
    popped at most once.
    """
    distances = {node: float("inf") for node in graph.get_all_nodes()}

    if start_node not in distances:
        return {}

    distances[start_node] = 0
    # min-heap of (distance, restaurant_id) so the closest unvisited node
    # is always popped first
    heap = [(0, start_node)]
    visited = set()

    while heap:
        current_distance, current_node = heapq.heappop(heap)

        # skip stale entries left in the heap from earlier relaxations
        if current_node in visited:
            continue
        visited.add(current_node)

        for neighbor, weight in graph.get_neighbors(current_node).items():
            if neighbor in visited:
                continue
            candidate_distance = current_distance + weight
            # relax the edge if we found a shorter path to neighbor
            if candidate_distance < distances[neighbor]:
                distances[neighbor] = candidate_distance
                heapq.heappush(heap, (candidate_distance, neighbor))

    return distances
