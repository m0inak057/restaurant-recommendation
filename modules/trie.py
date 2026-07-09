class TrieNode:
    def __init__(self):
        self.children = {}
        self.restaurant_ids = []


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, restaurant_id):
        """
        Insert a restaurant name into the trie, storing restaurant_id at every
        node along the path so prefix search can collect ids without a
        separate traversal to the leaf.

        Time complexity: O(L) where L is the length of word.
        """
        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            node.restaurant_ids.append(restaurant_id)

    def search_prefix(self, prefix):
        """
        Return all restaurant IDs whose names start with the given prefix
        (case-insensitive).

        Time complexity: O(P + K) where P is the length of prefix and K is
        the number of matching restaurant IDs (ids are collected directly
        from the node reached after walking the prefix, avoiding a subtree
        scan).
        """
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return []
            node = node.children[char]
        return list(node.restaurant_ids)
