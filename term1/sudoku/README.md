# Artificial Intelligence Nanodegree
## Introductory Project: Diagonal Sudoku Solver

# Question 1 (Naked Twins)
Q: How do we use constraint propagation to solve the naked twins problem?  
A: For each unit in the board, we do the following.
   * Identify naked twin pairs in the unit. To do this, we take all possible 2-combinations of boxes in the unit and
   for each pair, see if the pair is a naked-twin-pair. By definition, the pair is a naked twin if both boxes have the 
   same two possible values either of which can go into the boxes. As per the code nomenclature in the lab and submitted
   solution, this boils down to `values[box1] == values[box2] and len(values[box1]) == 2`
   * Once we have all naked twin pairs in a unit, for each pair `(box1,box2)`, we do the following:
      * Let `xy` be the two possible values of the twin pair. For all other boxes in the unit other than box1 and box2, 
       we remove `x` and `y` from the candidate list of that box. As per the submitted code, this comes down to :
       ```python
        for b1, b2 in twins:
            twin1 = (values[b1])[0]
            twin2 = (values[b1])[1]
            for u in unit:
                if u != b1 and u != b2:
                    new_val = values[u].replace(twin1, '').replace(twin2, '')
                    if values[u] != new_val:
                        assign_value(values, u, new_val)
       ```
   
# Question 2 (Diagonal Sudoku)
Q: How do we use constraint propagation to solve the diagonal sudoku problem?  
A: The diagonal sudoku problem is similar to the vanilla sudoku problem with just one conceptual addition - The two 
diagonals are now two additional units. When solving the original sudoku problem, (as done in the labs), we had computed
the units in a sudoku board. We now simply extend this computation so that the units in the board will comprise of the 
two diagonals (in addition to the other existing units like rows, columns, 3x3 sub grids)

```python
diag_units = [[''.join(e) for e in zip(rows, cols)], [''.join(e) for e in zip(rows, cols[::-1])]]
unitlist = row_units + column_units + square_units + diag_units
```

With the above unitlist, the rest of the solution is basically the same as the vanilla sudoku case. When enforcing any 
of the constraints like *elimination* or *only_choice* or *naked_twins* , the constraint propagation works with units 
and so will automatically pick up the two new diagonal units

### Install

This project requires **Python 3**.

We recommend students install [Anaconda](https://www.continuum.io/downloads), a pre-packaged Python distribution that contains all of the necessary libraries and software for this project. 
Please try using the environment we provided in the Anaconda lesson of the Nanodegree.

##### Optional: Pygame

Optionally, you can also install pygame if you want to see your visualization. If you've followed our instructions for setting up our conda environment, you should be all set.

If not, please see how to download pygame [here](http://www.pygame.org/download.shtml).

### Code

* `solutions.py` - You'll fill this in as part of your solution.
* `solution_test.py` - Do not modify this. You can test your solution by running `python solution_test.py`.
* `PySudoku.py` - Do not modify this. This is code for visualizing your solution.
* `visualize.py` - Do not modify this. This is code for visualizing your solution.

### Visualizing

To visualize your solution, please only assign values to the values_dict using the ```assign_values``` function provided in solution.py

### Data

The data consists of a text file of diagonal sudokus for you to solve.
