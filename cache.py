class ListNode(object):
    def __init__(self, data, prev, next):
        self.data = data
        self.next = next
        self.prev = prev


class LRUCache(object):
    def __init__(self, capacity):
        """Initialize a Least Recently Used cache with the given capacity."""
        if capacity <= 0:
            raise ValueError("Given capacity is too small!")
        # Use a dictionary for fast lookups. Map keys to a list containing
        # the value and a linked list node tracking LRU.
        self.map = {}
        # Implement a Queue using a linked list, to track and update LRU
        # Need a doubly-linked list so we can get the parent
        self._dummy_head = ListNode(0, None, None)
        self._tail = None
        self._capacity = capacity
        self._size = 0

    def get(self, key):
        """Get the value associated with the given cache key."""
        if key in self.map:
            value = self.map[key][0]
            node = self.map[key][1]
            # Update Queue using the following steps:
            # Update tail if current node is tail and there is more than one element in cache
            if self._tail == node and node.prev != self._dummy_head:
                self._tail = node.prev
            # Extract node from current position in Queue
            node.prev.next = node.next
            if node.next:
                node.next.prev = node.prev
            # Modify node's prev and next references
            node.prev, node.next = self._dummy_head, self._dummy_head.next
            # Transplant node into beginning of Queue
            if self._dummy_head.next is not None:
                self._dummy_head.next.prev = node
            self._dummy_head.next = node
            return value
        else:
            return None

    def set(self, key, value):
        """Set cache key to the given value."""
        # If key is in map, update the value and move node to front of queue
        evict = None
        if key in self.map:
            # Update value of key
            if isinstance(self.map[key][0], set):
                self.map[key][0].add(value)
            else:
                self.map[key][0] = value
            node = self.map[key][1]
            # Update Queue using the following steps:
            # Update tail if current node is tail and there is more than one element in cache
            if self._tail == node and node.prev != self._dummy_head:
                self._tail = node.prev
            # Extract node from current position in Queue
            node.prev.next = node.next
            if node.next:
                node.next.prev = node.prev
            # Modify node's prev and next references
            node.prev, node.next = self._dummy_head, self._dummy_head.next
            # Transplant node into beginning of Queue
            if self._dummy_head.next is not None:
                self._dummy_head.next.prev = node
            self._dummy_head.next = node
            return None
        elif self._size == self._capacity:
            # Evict LRU element using key of LRU
            lru = self._tail
            evict = (lru.data, self.map[lru.data][0])
            self.map.pop(lru.data)
            self._tail = lru.prev if lru.prev != self._dummy_head else None
            lru.prev.next = None
            self._size -= 1

        node = ListNode(key, self._dummy_head, self._dummy_head.next)
        if self._dummy_head.next is not None:
            self._dummy_head.next.prev = node
        self._dummy_head.next = node
        if self._tail is None:
            self._tail = node
        self.map[key] = [value, node]
        self._size += 1
        return evict