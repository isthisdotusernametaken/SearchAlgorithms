from abc import ABC, abstractmethod
from bisect import insort_left
from collections import deque


# Fringe data structures

# A Fringe tracks search statistics and, if needed, generates (when added) and
# uses heuristic information.
class Fringe(ABC):
    def __init__(self, uses_heuristic):
        super().__init__()
        self._uses_heuristic = uses_heuristic
        self._num_created = -1 # This makes the start not count for numCreated.
        self._max_fringe = 0

    @abstractmethod
    def __len__(self): # This allows bool() to be used for empty checking.
        pass

    @abstractmethod
    def _add(self, state):
        pass

    @abstractmethod
    def _remove(self):
        pass
    
    def add(self, state, goal):
        # Upon adding, if needed, the heuristic is calculated only once.
        if self._uses_heuristic:
            state.generate_heuristic(goal)
        
        self._add(state)
        self._num_created += 1

        if len(self) > self._max_fringe:
            self._max_fringe = len(self)

    # Because this method uses None to signal emptiness, a Fringe should not
    # contain None.
    def remove(self):
        return self._remove() if self else None
    
    @property
    def num_created(self):
        return self._num_created
    
    @property
    def max_fringe(self):
        return self._max_fringe

class Queue(Fringe):
    def __init__(self):
        super().__init__(False)
        self._deque = deque()
    
    def __len__(self):
        return len(self._deque)

    def _add(self, state):
        self._deque.append(state) # O(1)
    
    def _remove(self):
        return self._deque.popleft() # O(1)

class Stack(Fringe):
    def __init__(self):
        super().__init__(False)
        self._stack = []
    
    def __len__(self):
        return len(self._stack)

    def _add(self, state):
        self._stack.append(state) # O(1)
    
    def _remove(self):
        return self._stack.pop() # O(1)

# Note: A linked list would have O(log n) WC insert time (as opposed to
# O(n), dominated by shifting existing elements right) while maintaining O(1)
# removal time, but this was not implemented.
class PriorityQueue(Fringe):
    def __init__(self, f):
        super().__init__(True)
        self._sorted_list = []

        # f is negated so that the list is in descending order by f, making
        # removing the minimum O(1) by removing the end of the list.
        self._f = lambda state: -f(state)
    
    def __len__(self):
        return len(self._sorted_list)

    def _add(self, state):
        # Because removals are from the right, insort_left ensures that all
        # states with the same f-value are expanded in the order they arrived.
        insort_left(self._sorted_list, state, key=self._f) # O(n)
    
    def _remove(self):
        return self._sorted_list.pop() # O(1)


# Search algorithms

def BFS(start_state, goal_state):
    return _graph_search(start_state, goal_state, Queue())

# Note: By using a stack for the fringe and never expanding a node twice (which
# necessarily includes never expanding a node twice on the same path),
# backtracking and cycle protection are automatically implemented.
def DFS(start_state, goal_state):
    return _graph_search(start_state, goal_state, Stack())

def GBFS(start_state, goal_state):
    return _graph_search(start_state, goal_state, PriorityQueue(
        lambda state: state.heuristic # f(n) = h(n)
    ))

def AStar(start_state, goal_state):
    return _graph_search(start_state, goal_state, PriorityQueue(
        lambda state: state.depth + state.heuristic # f(n) = g(n) + h(n)
    ))

def _try_add(fringe, expanded, goal, node):
    # Only add the state if it is legal and not yet expanded.
    if node is not None and node not in expanded:
        fringe.add(node, goal)

# Notes:
#   The fringe defines the search strategy and should initially be empty.
#   Because each node is counted for numExpanded only once, even if it was
#       added to the fringe multiple times, the size of the expanded set
#       provides the value of numExpanded.
def _graph_search(start_state, goal_state, fringe):
    expanded = set()
    fringe.add(start_state, goal_state) # This does not count for numCreated.

    while fringe:
        # 1. Check if the node should be expanded.
        node = fringe.remove()

        if node in expanded:
            continue
        if node == goal_state: # Search succeeded
            return (
                node,
                node.depth, fringe.num_created, len(expanded), fringe.max_fringe
            )
        
        # 2. Expand the node.
        expanded.add(node)

        # Add all new, legal successor states to the fringe.
        _try_add(fringe, expanded, goal_state, node.space_up())
        _try_add(fringe, expanded, goal_state, node.space_down())
        _try_add(fringe, expanded, goal_state, node.space_left())
        _try_add(fringe, expanded, goal_state, node.space_right())
    
    return (None, -1, 0, 0, 0) # Search failed
