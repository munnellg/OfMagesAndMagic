class GameOfLife:
    ALIVE = 1 # Define the state of being alive using the number 1
    DEAD  = 0 # Define the state of being dead using the number  0

    # Create a new version of the game of life
    def __init__(self, width, height):
        # Create a grid of numbers and fill it with dead cells
        # I make the grid a little bigger than the user asked for because
        # it makes it easier to test for life and death
        self.cells = [ [self.DEAD]*(width+2) for i in range(height+2)]

        # Remember previous states so we can rewind
        self.memory = []

    # Count how many live cells surround the cell at (x,y)
    def __count_neighbours(self, x, y):
        # Our count starts at zero
        count = 0
        # Move around (x,y) in a square shape
        for y2 in range(y-1, y+2):
            for x2 in range(x-1, x+2):
                # Count any live cells we see
                count += self.cells[y2][x2]

        # Part of our count will actually count the cell at (x,y), which really
        # ought to be ignored, so just remove that one number from the result
        # before returning
        return count - self.cells[y][x]

    # Flips a cell from alive to dead or dead to alive
    def __flip(self, x, y):
        self.cells[y][x] = self.ALIVE-self.cells[y][x]

    # Determines whether or not a cell should flip from live to dead or from
    # dead to alive. The four rules of Conway's Game of Live which this
    # function tests are:
    #
    # 1. Any live cell with fewer than two live neighbours dies, as if caused
    #    by under-population.
    # 2. Any live cell with two or three live neighbours lives on to the next
    #    generation.
    # 3. Any live cell with more than three live neighbours dies, as if by
    #    over-population.
    # 4. Any dead cell with exactly three live neighbours becomes a live cell,
    #    as if by reproduction
    def __should_flip(self, x, y):
        # Count the cell's neighbours
        neighbours = self.__count_neighbours(x,y)

        # If the cell has the value 1, that means it's alive
        if self.cells[y][x] == self.ALIVE:
            # Test if live cell should die due to overpopulation/isolation
            if neighbours < 2 or neighbours > 3:
                return True
        elif self.cells[y][x] == self.DEAD: # If a cell isn't alive, then it's dead
            # If this dead cell has three neighbours, it should come to life
            if neighbours == 3:
                # If this cell has three neighbours, it should flip
                return True
        else:
            # None of the rules for changing the state of the cell were passed,
            # so this cell doesn't change
            return False


    # Set cell (x,y) to value
    def set_cell(self, x, y, value):
        # Need to offset because our grid is a bit bigger than requested
        self.cells[y+1][x+1] = value

    # Get value of cell (x,y)
    def get_cell(self, x, y):
        # Need to offset because our grid is a bit bigger than requested
        return self.cells[y+1][x+1]

    # Get the width of the grid without including our extensions
    def get_width(self):
        return len(self.cells[0])-2

    # Get the height of the grid without including our extensions
    def get_height(self):
        return len(self.cells)-2

    def reset(self):
        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                self.cells[y][x] = self.DEAD

    # Rewind the game of life by n_steps
    def rewind(self, n_steps):
        for i in range(0, min(n_steps, len(self.memory))):
            to_be_flipped = self.memory[-1]
            del self.memory[-1]
            for cell_position in to_be_flipped:
                self.__flip(*cell_position)

    # Advance the state of the game of life
    def update(self):
        # Flags will keep track of all cells that are either coming to life
        # or dying. We'll flip all of them at the same time at the end
        to_be_flipped = []

        #  Examine every individual cell in our grid
        for y in range(1, len(self.cells)-1):
            for x in range(1, len(self.cells[0])-1):
                # If this cell should flip (either from live to dead or dead to
                # live) then add them to our flags list
                if self.__should_flip(x, y):
                    to_be_flipped.append((x,y))

        # Go over all the cells that we decided to flip and switch their values
        for cell_position in to_be_flipped:
            self.__flip(*cell_position)

            
        # If we changed anything, remember it
        if len(to_be_flipped) > 0:
            self.memory.append(to_be_flipped)

            # Lazy method of capping memory limit.
            # Don't want long simulations to kill RAM
            if len(self.memory) > 10000:
                self.memory=self.memory[1:]

        return len(to_be_flipped) != 0

    # Override the default string method so we can make the game loop pretty
    # if we print it in the terminal
    def __str__(self):
        # text buffer
        text = ""

        # Build our string row by row
        for y in self.cells:
            text += "{}\n".format(y)

        # Return the text representation of our game
        return text
