import itertools

rows = 'ABCDEFGHI'
cols = '123456789'

def cross(a, b):
    return [s+t for s in a for t in b]

boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
diag_units = [[''.join(e) for e in zip(rows, cols)], [''.join(e) for e in zip(rows, cols[::-1])]]
unitlist = row_units + column_units + square_units + diag_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], []))-set([s])) for s in boxes)


assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """

    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
        Output: None
    """

    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

    pass

def eliminate(values):
    """Eliminate values from peers of each box with a single value.

     Go through all the boxes, and whenever there is a box with a single value,
     eliminate this value from the set of values of all its peers.

     Args:
         values: Sudoku in dictionary form.
     Returns:
         Resulting Sudoku in dictionary form after eliminating values.
     """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            assign_value(values, peer, values[peer].replace(digit, ''))
    return values


def only_choice(values):
    """Finalize all values that are the only choice for a unit.

     Go through all the units, and whenever there is a unit with a value
     that only fits in one box, assign the value to this box.

     Input: Sudoku in dictionary form.
     Output: Resulting Sudoku in dictionary form after filling in only choices.
     """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                assign_value(values, dplaces[0], digit)
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers

    for unit in unitlist:
        combos = [e for e in itertools.combinations(unit, 2)]
        twins = [(b1, b2) for b1, b2 in combos if ((sorted(values[b1]) == sorted(values[b2])) and len(values[b1]) == 2)]
        for b1, b2 in twins:
            twin1 = (values[b1])[0]
            twin2 = (values[b1])[1]
            for u in unit:
                if u != b1 and u != b2:
                    new_val = values[u].replace(twin1, '').replace(twin2, '')
                    if values[u] != new_val:
                        assign_value(values, u, new_val)

    return values


def reduce_puzzle(values):
    """
      Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
      If the sudoku is solved, return the sudoku.
      If after an iteration of both functions, the sudoku remains the same, return the sudoku.
      Input: A sudoku in dictionary form.
      Output: The resulting sudoku in dictionary form.
      """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        for strategy in [eliminate, only_choice, naked_twins]:
            values = strategy(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def verify(values) :
    """
    Verify that the solved board values has really been solved
    :param values: Solved sudoku board
    :return: True if solution is valid and False if not
    """
    for unit in unitlist:
        if len(set(values[elem] for elem in unit)) != 9:
            return False

    return True


def search(values):
    """
    Apply DFS to split and solve a stalled sudoku board
    """

    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False  # Failed earlier
    if all(len(values[s]) == 1 for s in boxes):
        if verify(values):
            return values  # Solved!
        else:
            print("Erroneous solution reported. Exiting.")
            display(values)
            exit(0)

    # Choose one of the unfilled squares with the fewest possibilities
    n, s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    board = grid_values(grid)
    return search(board)


if __name__ == '__main__':

    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    solved = solve(diag_sudoku_grid)

    if not solved:
        print("No solution could be found")
    else:
        try:
            from visualize import visualize_assignments
            visualize_assignments(assignments)

        except SystemExit:
            pass
        except:
            print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
            display(solved)
