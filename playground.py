import random
from minesweeper import *

def neighbours(cell):
    neighbour_cells = set()
    for i in range(cell[0] - 1, cell[0] + 2):
        for j in range(cell[1] - 1, cell[1] + 2):
            # Ignore the cell itself
            if (i, j) == cell:
                continue
            # Update count if cell in bounds and is mine
            if 0 <= i < 8 and 0 <= j < 8:
                neighbour_cells.add((i, j))
    return neighbour_cells


# print(neighbours((0, 4)))

mines = {(2, 0)}
safes = set()
safes.add((2, 0))
print(type(safes))
print(safes)
cells = {(2, 0), (3, 3), (1, 0)}
print(type(cells))

print(cells - safes)
