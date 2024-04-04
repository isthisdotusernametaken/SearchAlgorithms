# General notes:
#       Python 3.12.0 was used for this project, and older versions may not
#           provide all the required features. For example, versions before
#           3.10 will not accept a key argument for insort_left, so these
#           versions will not be able to run GBFS or AStar.
#       Read-only properties are preferred over bare variables when values
#           should not be externally modified.
#       Depth is measured by edges.
# Style (mostly based on PEP 8 - Style Guide for Python Code):
#       Class names use the CapWords convention.
#       Function and variable names (including field names) use snake_case. To
#           match the convention used elsewhere for the search algorithm
#           abbreviations, the search algorithm functions are excepted.
#       Fields intended for use only within their class, as well as other
#           variables and functions intended for use only within their file,
#           begin with a single underscore.
#       Non-field variables intended to be constant use all uppercase with
#           underscores between words.
#       Logical groupings of functions or statements within the least-indented
#           code level of a class or file are each headed with two blank lines,
#           followed by a comment with the section's title, followed by a blank
#           line before the section's content.

from inspect import cleandoc
import sys

from Board import BadBoard, SlideBoard
from Solver import BFS, DFS, GBFS, AStar


# Utility constants

_README = "Readme.txt"
_ALGORITHMS = {"BFS": BFS, "DFS": DFS, "GBFS": GBFS, "AStar": AStar}
_MIN_SIZE = 2
_MAX_SIZE = 9

# These also serve as lists of valid characters for each size.
_GOALS = {}
_GOALS[2] = "213 "
_GOALS[3] = " 12345678"
_GOALS[4] = "123456789ABCDEF "
_GOALS[5] = " 123456789ABCDEFGHIJKLMNO"
_GOALS[6] = " 123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_GOALS[7] = " 123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklm"
_GOALS[8] = " 123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@"
_GOALS[9] = " 123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()-_=+[{]}|"


# Argument validation and processing

# Exceptions from this function should include error messages defined by this
# program, so error messages should be suitable for printing.
# RuntimeError, ValueError, and BadBoard must be handled by the caller.
def _parse_args():
    if len(sys.argv) != 4:
        raise RuntimeError(
            "Exactly three arguments are required: "
            "size initialstate searchmethod"
        )
    
    # 1. Size
    try:
        size = int(sys.argv[1])
    except:
        raise ValueError(f'"{sys.argv[1]}" is not a valid integer.')
    
    if size < _MIN_SIZE or size > _MAX_SIZE:
        raise ValueError(
            f"The size must be in the range [{_MIN_SIZE}, {_MAX_SIZE}]."
        )
    
    # 2. Initial state (valid characters)
    if len(set(sys.argv[2])) != len(_GOALS[size])\
       or any([char not in _GOALS[size] for char in sys.argv[2]]):
        raise ValueError(
            f'A board of size {size} must include exactly one of each of the '
            f'following characters: "{_GOALS[size]}".'
        )

    # The above checks should avoid BadBoard exceptions, but they should be
    # caught anyway in case the Board module changes in the future.
    # Solvability is not checked, as the professor deemed it unnecessary.
    initial_state = SlideBoard.create(sys.argv[2], size)

    # 3. Search method
    algorithm_name = sys.argv[3]
    try:
        algorithm = _ALGORITHMS[algorithm_name]
    except KeyError:
        raise ValueError(
            f'"{algorithm_name}" is not a supported algorithm. Choose one of '
            f'the following: {" ".join(_ALGORITHMS.keys())}'
        )

    return (size, initial_state, algorithm_name, algorithm)


# Searching and printing output

# I tested three versions of this method: (1) appending each solution node's
# tiles to the front of a single string at each step up the tree and then
# printing that string at the end, (2) forming a linked list within the tree
# (with an extra field in each solution node) and then printing the steps while
# traversing that list, and (3) appending each solution node to an explicit
# list and printing the steps while traversing it in reverse (this solution).
#
# In my tests for sizes 3-4, implementations 2 and 3 were always ~2-4x faster
# than implementation 1 for the total program runtime, but I found no
# consistent runtime differences between implementations 2 and 3.
# Implementation 3 was chosen over implementation 2 to avoid unnecessarily
# giving different objects of the same class different externally accessible
# members.
def _print_solution(node): # To console
    if node is None:
        print("No solution found.")
    else:
        solution = []
        while node is not None:
            solution.append(node)
            node = node.parent
        for solution_node in reversed(solution):
            print(f'"{solution_node.tiles}"')

def _print_result(size, start, goal, algorithm_name,
                  depth, num_created, num_expanded, max_fringe): # To readme
    try:
        with open(_README, "a") as readme:
            readme.write(cleandoc(f"""
                size: {size}
                initial: "{start}"
                goal: "{goal}"
                searchmethod: {algorithm_name}
                {depth}, {num_created}, {num_expanded}, {max_fringe}
                {"*" * 32}
            """))
            readme.write("\n")
    except OSError:
        print(
            f'The results could not be written to "{_README}". Make sure the '
            'program is run with sufficient permissions.'
        )
    
def main():
    try:
        size, start, algorithm_name, algorithm = _parse_args()
    except (RuntimeError, ValueError, BadBoard) as e:
        print("Invalid input:", e)
        return -1

    try:
        goal = SlideBoard.create(_GOALS[size], size)
    except:
        print("Program error: The goal state could not be created.")
        return -1
    

    node, *stats = algorithm(start, goal)

    _print_solution(node)
    _print_result(size, start.tiles, goal.tiles, algorithm_name, *stats)

if __name__ == "__main__":
    main()
