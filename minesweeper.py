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

        # returns mines or empty set
        mines = set()
        if self.count == len(self.cells) and self.count > 0:
            mines = self.cells
        return mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """

        # count is 0 and all cells are safe in this sentence
        safes = set()
        if self.count == 0:
            safes = self.cells
        return safes

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # check cell in sentence cells, remove, reduce mines count by 1
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1


    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """

        # check cell in sentence cells, remove
        if cell in self.cells:
            self.cells.remove(cell)

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

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)
            
    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.
        """
        # mark the cell as one of the moves made in the game
        self.moves_made.add(cell)
        # mark the cell as a safe cell, updating any sentences that contain the cell as well
        self.mark_safe(cell)
        # add a new sentence to the AI’s knowledge base, based on the value of cell and count, to indicate that count of the cell’s neighbors are mines. 
        neighbour_cells = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if (i, j) == cell:
                    continue
                # Only include cells whose state is still undetermined in the sentence
                if (i, j) in self.safes:
                    continue
                if (i, j) in self.mines:
                    count -= 1
                    continue
                if 0 <= i < self.height and 0 <= j < self.width:
                    neighbour_cells.add((i, j))

        # create new sentence, ignore if empty
        new_sentence = Sentence(neighbour_cells, count)
        # add sentence to knowledge
        self.knowledge.append(new_sentence)
        # create a copy of knowledge
        current_knowledge = self.knowledge.copy()
        # update knowledge
        self.update()

        # loop over knowledge and update till no new knowledge inferred
        while current_knowledge != self.knowledge:
            current_knowledge = self.knowledge
            self.update()
        
    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        available_moves = []
        for sentence in self.knowledge:
            for cell in sentence.cells:
                if cell not in self.moves_made and cell not in self.mines:
                    available_moves.append(cell)
        try:
            return random.choice(available_moves)
        except IndexError:
            return None

    def update(self):
        """
        Update knowledge and make new inferences from available knowledge by adding new sentences when possible.
        """
        # draw new inferences that weren’t possible before
     
        for sentence in self.knowledge:
            self.safes.update(sentence.known_safes())
            self.mines.update(sentence.known_mines())

        # If, based on any of the sentences in self.knowledge, new cells can be marked as safe or as mines
        if self.safes:
            for safe in self.safes:
                self.mark_safe(safe)
        if self.mines:
            for mine in self.mines:
                self.mark_mine(mine)
        # If, based on any of the sentences in self.knowledge, new sentences can be inferred, then those sentences should be added to the knowledge base as well
        # Remove any empty sentences from knowledge base:
        empty = Sentence(set(), 0)

        self.knowledge[:] = [x for x in self.knowledge if x != empty]
        for current_sentence in self.knowledge:
            for next_sentence in self.knowledge:
                if current_sentence != next_sentence and current_sentence.cells.issubset(next_sentence.cells):
                    new_cells = next_sentence.cells - current_sentence.cells
                    new_count = next_sentence.count - current_sentence.count
                    new_sentence = Sentence(new_cells, new_count)
                    if new_sentence not in self.knowledge:
                        self.knowledge.append(new_sentence)


            