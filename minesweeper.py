import itertools
import random


class Minesweeper:
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence:
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        mines = set()
        if self.count == len(self.cells):
            mines = self.cells
        return mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        safes = set()
        if self.count == 0:
            safes = self.cells
        return safes

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.count -= 1
            self.cells.remove(cell)

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)

    def neighbours(self, cell):
        minesweeper = Minesweeper()
        neighbour_cells = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # Ignore the cell itself
                if (i, j) == cell:
                    continue
                # Update count if cell in bounds and is mine
                if 0 <= i < minesweeper.height and 0 <= j < minesweeper.width:
                    neighbour_cells.add((i, j))
        return neighbour_cells


class MinesweeperAI:
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()
        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)
            if len(sentence.cells) == 0:
                self.knowledge.remove(sentence)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)
            if len(sentence.cells) == 0:
                self.knowledge.remove(sentence)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.
        """
        # mark the cell as one of the moves made in the game.
        self.moves_made.add(cell)
        # mark the cell as a safe cell, updating any sentences that contain the cell as well.
        self.mark_safe(cell)
        # add a new sentence to the AI’s knowledge base, based on the value of cell and count, to indicate that count of the cell’s neighbors are mines. Be sure to only include cells whose state is still undetermined in the sentence.
        neighbour_cells = self.neighbours(cell)
        # mark mines and safes
        # check knowledge again
        # Exclude known safes and mines from the new sentence
        known_mines = neighbour_cells & self.mines
        known_safes = neighbour_cells & self.safes
        count -= len(known_mines)  # Adjust count by subtracting the number of known mines

        # Remove known mines and safes from neighbour_cells
        neighbour_cells -= (known_mines | known_safes)
        if len(self.knowledge) > 0:
            for sentence in self.knowledge:
                self.safes.update(sentence.known_safes())
                self.mines.update(sentence.known_mines())
        self.mark_cells(neighbour_cells, count)
        # remove known mines and safes then create new sentence
        neighbour_cells = neighbour_cells - self.mines - self.safes
        new_sentence = Sentence(neighbour_cells, count)

        # add sentence to knowledge
        if new_sentence not in self.knowledge:
            self.knowledge.append(new_sentence)

        # create new knowledge
        new_knowledge = []
    
        for sub_set in self.knowledge:
            for super_set in self.knowledge:
                if sub_set != super_set and sub_set.cells.issubset(super_set.cells):
                    new_cells = super_set.cells - sub_set.cells
                    new_count = super_set.count - sub_set.count
                    if len(new_cells) > 0 and new_count >= 0:
                        # If, based on any of the sentences in self.knowledge, new cells can be marked as safe or as mines, then the function should do so.
                        self.mark_cells(new_cells, new_count)
                        updated_sentence = Sentence(new_cells, new_count)
                        if (updated_sentence not in new_knowledge and len(updated_sentence.cells) != 0):
                            new_knowledge.append(updated_sentence)
        for sentence in new_knowledge:
            if sentence not in self.knowledge and len(sentence.cells) != 0:
                self.knowledge.append(sentence)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # return a move from self.safes that is not in moved made
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        # If no safe move can be guaranteed, the function should return None.
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # create a list with moves that are available and not mines
        available_moves = []
        for sentence in self.knowledge:
            for cell in sentence.cells:
                if cell not in self.moves_made and cell not in self.mines:
                    available_moves.append(cell)
        # If no such moves are possible, the function should return None
        try:
            return random.choice(available_moves)
        except IndexError:
            return None

    def neighbours(self, cell):
        neighbour_cells = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # Ignore the cell itself
                if (i, j) == cell:
                    continue
                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    neighbour_cells.add((i, j))
        return neighbour_cells


    def mark_cells(self, cells, count):
        if count == 0:
            self.safes.update(cells)
            for cell in cells:
                self.mark_safe(cell)

        elif count == len(cells):
            self.mines.update(cells)
            for cell in cells:
                self.mark_mine(cell)

    