class RestaurantGraph:
    def __init__(self):
        """
        Initialize an empty graph backed by an adjacency list
        (dict of dicts): {restaurant_id: {neighbor_id: weight}}.

        Time complexity: O(1)
        Space complexity: O(1)
        """
        self.adjacency_list = {}

    def add_node(self, restaurant_id):
        """
        Add a restaurant as a node in the graph, if not already present.

        Time complexity: O(1)
        Space complexity: O(1) per call, O(V) total across all nodes.
        """
        if restaurant_id not in self.adjacency_list:
            self.adjacency_list[restaurant_id] = {}

    def add_edge(self, id1, id2, weight):
        """
        Add a weighted, undirected edge between two restaurants, where
        weight is a similarity score between 0.0 and 1.0. Adds either node
        that does not already exist.

        Time complexity: O(1)
        Space complexity: O(1) per call, O(E) total across all edges.
        """
        self.add_node(id1)
        self.add_node(id2)
        self.adjacency_list[id1][id2] = weight
        self.adjacency_list[id2][id1] = weight

    def get_neighbors(self, restaurant_id):
        """
        Return a dict of {neighbor_id: weight} for all restaurants
        connected to the given restaurant_id.

        Time complexity: O(1) to fetch the dict reference (O(k) if a copy
        of the k neighbors is required by the caller).
        Space complexity: O(1), returns a reference to the stored dict.
        """
        return self.adjacency_list.get(restaurant_id, {})

    def get_all_nodes(self):
        """
        Return all restaurant IDs currently stored in the graph.

        Time complexity: O(V) where V is the number of nodes.
        Space complexity: O(V) for the returned list.
        """
        return list(self.adjacency_list.keys())
