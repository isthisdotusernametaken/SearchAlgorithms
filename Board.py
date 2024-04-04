# In the 1D row-major order representation used, a tile's index contains its
# coordinates in the value c = ny + x, and the coordinates can be extracted as
# (c mod n, c div n). The formula for the Manhattan distance between two tiles
# is |y2-y1| + |x2-x1|.
def _manhattan_distance(first, second):
    total_manhattan = 0
    for ind, tile in enumerate(first.tiles):
        if tile == " ":
            continue # The blank space is not counted
        
        y1, x1 = divmod(ind, first.n)
        y2, x2 = divmod(second.tiles.index(tile), first.n)
        total_manhattan += abs(y2 - y1) + abs(x2 - x1)
    
    return total_manhattan


# Indicate a requested board is invalid at instantiation.
class BadBoard(ValueError):
    pass

# To use this class, call create(str_rep, n) to build an initial state, and if
# no BadBoard exception is raised, use the following interface:
#   Successor functions (return new boards connected to the tree):
#       space_up(), space_down(), space_left(), space_right()
#   Read-only properties:
#       tiles, n, depth, parent, heuristic
#   Generate the heuristic value for a specific goal:
#       generate_heuristic(goal)
class SlideBoard:
    # str_rep: String representation of an n x n board in row-major order
    # n: Board width
    # 
    # Although this class is ambivalent to the use of non-alphanumeric
    # characters in str_rep, the testing program has character-validity
    # restrictions. BadBoard exceptions may be avoided by checking in Tester.
    # The create method is provided to make a start state, and the movement
    # methods bypass this method to avoid overhead from unnecessary checks.
    @classmethod
    def create(cls, str_rep, n):
        if n <= 0:
            raise BadBoard("Board size must be positive.")
        if len(str_rep) != n * n:
            raise BadBoard("An n x n board must specify n^2 spaces.")
        if " " not in str_rep:
            raise BadBoard("A board must include a blank space (space key).")
        if len(set(str_rep)) != len(str_rep):
            raise BadBoard("A board must have no duplicate tiles.")
        
        return cls(str_rep, n, str_rep.index(" "), 0, None)

    def __init__(self, tiles, n, space_ind, depth, parent):
        self._tiles = tiles

        # Fields for managing the blank space's movement
        self._n = n
        self._space_ind = space_ind
        
        # Field for an optional heuristic value (not generated automatically so
        # that unnecessary work is avoided for uninformed searches)
        self._heuristic = None

        # Fields for recording the search's tree
        self._depth = depth
        self._parent = parent

    # The equality operator is used to check values against the expanded set.
    # Only the tiles are relevant to whether a state has been expanded already.
    def __eq__(self, other):
        return type(self) == type(other) and self.tiles == other.tiles
    
    def generate_heuristic(self, goal):
        self._heuristic = _manhattan_distance(self, goal)
    
    # The hash value supports the use of a hash table for the expanded set.
    def __hash__(self):
        return hash(self.tiles)
    

    # Successor functions

    def _space_move(self, check, new_pos):
        if not check: # Illegal move
            return None

        min_pos = min(self._space_ind, new_pos)
        max_pos = max(self._space_ind, new_pos)

        # Copy the state string with the space and its target swapped, and
        # return it in a new board object.
        return SlideBoard(
            self.tiles[:min_pos] + self.tiles[max_pos]\
               + self.tiles[min_pos+1:max_pos] + self.tiles[min_pos]\
               + self.tiles[max_pos+1:],
            self.n, new_pos, # new_pos is the new spaceInd.
            self.depth + 1, self # Add the new state to the tree.
        )

    def space_up(self):
        # The first row has indices 0 to n - 1.
        return self._space_move(
            self._space_ind >= self.n,
            self._space_ind - self.n
        )
    
    def space_down(self):
        # The last row has indices n^2-n to n^2-1.
        return self._space_move(
            self._space_ind < self.n ** 2 - self.n,
            self._space_ind + self.n
        )

    def space_left(self):
        # The first column has indices 0, n, 2n, 3n, ....
        return self._space_move(
            self._space_ind % self.n != 0,
            self._space_ind - 1
        )

    def space_right(self):
        # The last column has indices n-1, 2n-1, 3n-1, 4n-1, ....
        return self._space_move(
            self._space_ind % self.n != self.n - 1,
            self._space_ind + 1
        )


    # Accessor properties

    @property
    def tiles(self):
        return self._tiles

    @property
    def n(self):
        return self._n

    # depth is also the total path cost because all actions have cost 1.
    @property
    def depth(self): 
        return self._depth

    @property
    def parent(self):
        return self._parent
    
    @property
    def heuristic(self):
        return self._heuristic
