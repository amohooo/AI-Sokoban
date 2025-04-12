'''

    Sokoban assignment


The functions and classes defined in this module will be called by a marker script. 
You should complete the functions and classes according to their specified interfaces.

No partial marks will be awarded for functions that do not meet the specifications
of the interfaces.

You are NOT allowed to change the defined interfaces.
In other words, you must fully adhere to the specifications of the 
functions, their arguments and returned values.
Changing the interfacce of a function will likely result in a fail 
for the test of your code. This is not negotiable! 

You have to make sure that your code works with the files provided 
(search.py and sokoban.py) as your code will be tested 
with the original copies of these files. 

Last modified by 2022-03-27  by f.maire@qut.edu.au
- clarifiy some comments, rename some functions
  (and hopefully didn't introduce any bug!)

'''

# You have to make sure that your code works with 
# the files provided (search.py and sokoban.py) as your code will be tested 
# with these files
import itertools

#import numpy
import search
from search import PriorityQueue
from sokoban import Warehouse
from collections import deque
from search import astar_graph_search


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def my_team():
    '''
    Return the list of the team members of this assignment submission as a list
    of triplet of the form (student_number, first_name, last_name)
    
    '''
    return [(11427591, 'Mohan', 'Hao')]

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

directions = {'Up': (0, -1), 'Down': (0, 1), 'Left': (-1, 0), 'Right': (1, 0)} # Define movement directions

def taboo_cells(warehouse):
    '''  
    Identify the taboo cells of a warehouse. A "taboo cell" is by definition
    a cell inside a warehouse such that whenever a box get pushed on such 
    a cell then the puzzle becomes unsolvable. 
    
    Cells outside the warehouse are not taboo. It is a fail to tag an 
    outside cell as taboo.
    
    When determining the taboo cells, you must ignore all the existing boxes, 
    only consider the walls and the target  cells.  
    Use only the following rules to determine the taboo cells;
     Rule 1: if a cell is a corner and not a target, then it is a taboo cell.
     Rule 2: all the cells between two corners along a wall are taboo if none of 
             these cells is a target.
    
    @param warehouse: 
        a Warehouse object with the worker inside the warehouse

    @return
       A string representing the warehouse with only the wall cells marked with 
       a '#' and the taboo cells marked with a 'X'.  
       The returned string should NOT have marks for the worker, the targets,
       and the boxes.  
    '''
    def warehouse_to_grid(wh):
        """
        Converts the warehouse layout to a grid format.
        
        Args:
            warehouse: A Warehouse object.
            
        Returns:
            A list of lists where each sublist represents a row of the warehouse.
        """
        
        # Convert the warehouse layout to a grid format
        return [list(row) for row in str(wh).split('\n')] # Split the warehouse string by newline characters
    
    def is_target(grid, x, y):
        """
        Determines if a given cell is a target cell.
        
        Args:
            grid: The warehouse grid.
            x: The x-coordinate of the cell.
            y: The y-coordinate of the cell.
        
        Returns:
            True if the cell is a target, otherwise False.
        """
        
        # Check if the cell is a target
        return grid[y][x] in ['.', '!', '*'] # Target cells are '.', '!', or '*'
    
    def is_corner(grid, x, y):
        """
        Checks if a cell is a corner, which is defined as an empty space adjacent to two perpendicular walls.
        
        Args:
            grid: The warehouse grid.
            x: The x-coordinate of the cell.
            y: The y-coordinate of the cell.
        
        Returns:
            True if the cell is a corner and not a target, otherwise False.
        """
        if grid[y][x] != ' ': # Only consider empty cells for corners
            
            # Return False if the cell is not a corner
            return False
        # Define the valid configurations for internal corners
        valid_configurations = [
            ('Left', 'Up'),  # West and North
            ('Right', 'Up'),   # East and North
            ('Left', 'Down'),   # West and South
            ('Right', 'Down')     # East and South
        ]
        # Check if the cell is an internal corner based on the wall configuration
        for dir1, dir2 in valid_configurations:
            dx1, dy1 = directions[dir1] # Get the direction for the first wall
            dx2, dy2 = directions[dir2] # Get the direction for the second wall
            if 0 <= x + dx1 < len(grid[0]) and 0 <= y + dy1 < len(grid) and grid[y + dy1][x + dx1] == '#' and \
            0 <= x + dx2 < len(grid[0]) and 0 <= y + dy2 < len(grid) and grid[y + dy2][x + dx2] == '#':
                return True  # The cell is an internal corner based on wall configuration
        
        # Return False if the cell is not a corner
        return False 
    
    def is_wall(x, y):
        ''' 
        Check if a cell is a wall 
        '''
        # Check if the cell is within the grid and is a wall
        return 0 <= x < len(grid[0]) and 0 <= y < len(grid) and grid[y][x] == '#' # Check if the cell is a wall

    def get_valid_cells(grid):
        """
        Determines all accessible cells in the warehouse starting from the worker's position.
        
        Args:
            grid: The warehouse grid.
        
        Returns:
            A set of valid cells that can be reached from the worker's position.
        """
        valid_cells = set() # Initialize a set to store valid cells
        queue = [warehouse.worker] # Initialize a queue with the worker's position
        # Perform a breadth-first search to find all valid cells
        while queue:
            current = queue.pop(0) # Pop the current cell from the queue
            # Check if the current cell is not already visited and is not a wall
            if current not in valid_cells:
                valid_cells.add(current) # Add the current cell to the set of valid cells
                # Iterate through each direction
                for direction in directions.values():
                    next_cell = (current[0] + direction[0], current[1] + direction[1]) # Calculate the next cell
                    # Check if the next cell is not a wall and not already visited
                    if next_cell not in warehouse.walls and next_cell not in valid_cells:
                        queue.append(next_cell) # Add the next cell to the queue
        
        # Return the set of valid cells
        return valid_cells

    def mark_taboo_cells(valid_cells):
        """
        Marks the taboo cells based on the corners and cells between corners along the walls.
        
        Args:
            warehouse: The warehouse object containing walls and other structures.
            get_valid_cells: Function to retrieve accessible cells.
        
        Returns:
            A set of tuples representing the coordinates of taboo cells.
        """
        taboo_cells = set() # Initialize a set to store taboo cells
        # Iterate through each valid cell
        for x, y in valid_cells:
            # Check if the cell is a corner and not a target
            if is_corner(grid, x, y) and not is_target(grid, x, y):
                taboo_cells.add((x, y)) # Add the cell to the set of taboo cells
            # Iterate through each valid cell
            if is_corner(grid, x, y) and not is_target(grid, x, y):
                taboo_cells.add((x, y)) # Add the cell to the set of taboo cells
        # Iterate through each valid cell
        for x, y in valid_cells:
            # Check if the cell is a corner and not a target
            if (x, y) not in taboo_cells:
                # Iterate through each direction
                for direction in directions.values(): 
                    nx, ny = x + direction[0], y + direction[1] # Calculate the next cell
                    # Check if the next cell is a corner and not a target
                    while (nx, ny) in valid_cells:
                        # Check if the next cell is a corner and not a target
                        if is_corner(grid, nx, ny) or is_wall(nx, ny):
                            break # Break the loop if the next cell is a corner or a wall
                        nx += direction[0] # Update the x-coordinate
                        ny += direction[1] # Update the y-coordinate
                        
        # Return the set of taboo cells
        return taboo_cells

    def taboo_cells_to_string(grid):
        """
        Converts the grid with taboo cells into a string format.
        
        Args:
            grid: The warehouse grid modified with taboo cells.
        
        Returns:
            A string representation of the grid.
        """
        return '\n'.join(''.join(row).replace('.', ' ').replace('!', ' ').replace('*', ' ')
                     .replace('@', ' ').replace('$', ' ') for row in grid) # Replace target, worker, and box characters with empty spaces
        
    grid = warehouse_to_grid(warehouse) # Convert the warehouse layout to a grid
    valid_cells = get_valid_cells(grid) # Get the valid cells in the warehouse
    taboo = mark_taboo_cells(valid_cells) # Mark the taboo cells in the warehouse
    # Iterate through each taboo cell
    for x, y in taboo:
        if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
            grid[y][x] = 'X'  # Mark the cell as a taboo cell
    taboo_cells_str = taboo_cells_to_string(grid) # Convert the grid with taboo cells to a string
    
    # Return the string representation of the warehouse with taboo cells marked
    return taboo_cells_str
    

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class SokobanPuzzle(search.Problem):
    '''
    An instance of the class 'SokobanPuzzle' represents a Sokoban puzzle.
    An instance contains information about the walls, the targets, the boxes
    and the worker.

    Your implementation should be fully compatible with the search functions of 
    the provided module 'search.py'. 
    
    '''
    
    #
    #         "INSERT YOUR CODE HERE"
    #
    #     Revisit the sliding puzzle and the pancake puzzle for inspiration!
    #
    #     Note that you will need to add several functions to 
    #     complete this class. For example, a 'result' method is needed
    #     to satisfy the interface of 'search.Problem'.
    #
    #     You are allowed (and encouraged) to use auxiliary functions and classes

    
    def __init__(self, initial, push_costs=None):
        """
        Initializes a new instance of the Sokoban puzzle game state.
        
        Args:
            initial: An object representing the initial state of the warehouse.
                    Must have properties like 'worker', 'boxes', 'targets', and 'walls'.
            push_costs: Optional; a list of costs associated with pushing each box. If not provided,
                        all pushes are considered to have a uniform cost.

        Properties:
            initial: Tuple containing the initial position of the worker and the set of all boxes with their weights.
            warehouse: Stores the entire state of the warehouse including walls and spaces.
            goal: Target positions within the warehouse.
            walls: Set containing the positions of all walls in the warehouse.
            boxes: A frozenset of tuples where each tuple contains a box position and its weight.
            weights: List of weights for each box; defaults to zero if not provided.
            box_weights: Dictionary mapping each box's position to its weight for quick lookup.
            taboo_cells: Set of positions marked as taboo based on the warehouse configuration.
            _action_cache: Cache to store potential actions for a given state to speed up computation.
            _result_cache: Cache to store results of state transitions, reducing redundant calculations.
        """
        self.initial = (initial.worker, frozenset((pos, weight) for pos, weight in zip(initial.boxes, initial.weights))) # Store the initial state
        self.warehouse = initial # Store the warehouse state
        self.goal = initial.targets # Store the target positions
        self.walls = initial.walls # Store the walls of the warehouse
        self.boxes = frozenset((pos, weight) for pos, weight in zip(initial.boxes, initial.weights)) # Store boxes as a frozenset
        taboo_cell_str = taboo_cells(self.warehouse) # Get the taboo cells for the warehouse
        self.taboo_cells = set()  # This will store taboo cell coordinates
        self.extract_cells(taboo_cell_str) # Extract taboo cells from the string representation
        self._action_cache = {}  # Cache to store actions for given states
        self._result_cache = {}  # Cache to store results of state transitions
        
    def extract_cells(self, taboo_str):
        """
        Extracts and records the positions of taboo cells from a string representation of the warehouse.
        
        Args:
            taboo_str: String representation where 'X' marks a taboo cell.
        """
        rows = taboo_str.split('\n') # Split the string by newline characters
        # Iterate through each row in the warehouse
        for y, row in enumerate(rows):
            # Iterate through each character in the row
            for x, char in enumerate(row):
                if char == 'X': # Check if the cell is marked as a taboo cell
                    self.taboo_cells.add((x, y)) # Add the cell to the set of taboo cells
                    
    def actions(self, state):
        """
        Generates all possible actions from a given state.
        Uses set operations for faster lookups and simplified logic.
        """
        worker_pos, boxes = state
        box_positions = {pos for pos, _ in boxes}
        valid_actions = []
        
        for action, (dx, dy) in directions.items():
            next_pos = (worker_pos[0] + dx, worker_pos[1] + dy)
            
            # Check if next position is valid
            if not (0 <= next_pos[0] < self.warehouse.ncols and 0 <= next_pos[1] < self.warehouse.nrows):
                continue
            if next_pos in self.walls:
                continue
                
            # If next position has a box, check if it can be pushed
            if next_pos in box_positions:
                next_box_pos = (next_pos[0] + dx, next_pos[1] + dy)
                if (0 <= next_box_pos[0] < self.warehouse.ncols and 
                    0 <= next_box_pos[1] < self.warehouse.nrows and
                    next_box_pos not in self.walls and 
                    next_box_pos not in box_positions and
                    next_box_pos not in self.taboo_cells):
                    valid_actions.append(action)
            else:
                valid_actions.append(action)
                
        return valid_actions
    
    def result(self, state, action):
        """
        Computes the result of applying a specified action to the current state and caches it.
        Handles worker movement and box movement if a box is pushed by the worker.

        Args:
            state (tuple): The current state of the game, comprising the worker's position and the set of boxes with their weights.
            action (str): The action to apply; one of 'Up', 'Down', 'Left', 'Right'.

        Returns:
            tuple: The new state after the action has been applied.
        """
        # Check if the result is already computed and stored in the cache
        if (state, action) in self._result_cache:
            return self._result_cache[(state, action)]  # Return the cached result
        # Mapping from actions to changes in coordinate (dx, dy)
        worker_position, boxes = state # Unpack the state into worker position and boxes
        dx, dy = directions[action] # Get the change in coordinates for the action
        new_worker_pos = (worker_position[0] + dx, worker_position[1] + dy) # Calculate the new worker position
        # Check if the new worker position is a wall; if so, return the same state.
        if new_worker_pos in self.walls:
            self._result_cache[(state, action)] = state # Cache the result
            return state # Return the same state if the worker cannot move
        new_boxes = set() # Initialize a new set to store the updated box positions
        for box_pos, weight in boxes: # Iterate through each box position and weight
            # Check if the worker is pushing the box
            if box_pos == new_worker_pos:
                new_box_pos = (box_pos[0] + dx, box_pos[1] + dy) # Calculate the new box position
                # Check if the new box position is not a wall and not occupied by another box
                if new_box_pos not in self.walls and all(new_box_pos != other[0] for other in boxes):
                    new_boxes.add((new_box_pos, weight)) # Add the new box position to the set
                else:
                    new_boxes.add((box_pos, weight)) # Add the current box position if the box cannot be moved
            else:
                new_boxes.add((box_pos, weight)) # Add the current box position if the worker is not pushing the box

        result_state = (new_worker_pos, frozenset(new_boxes)) # Store the new worker position and updated box positions
        self._result_cache[(state, action)] = result_state # Cache the result
        
        # Return the new state after applying the action
        return result_state
    
    def goal_test(self, state):
        """
        Check if the current state satisfies the goal condition: all boxes are on target positions.

        Parameters:
        state (tuple): The state to test, structured as (worker_position, frozenset(boxes_positions))

        Returns:
        bool: True if all boxes are on their respective target positions, otherwise False.
        """
        # Convert box locations and target locations to sets for comparison
        _, boxes = state
        box_positions = {box[0] for box in boxes}  # Extract only positions
        targets = set(self.goal) # Convert target locations to a set
        
        # Check if all boxes are on target positions
        return box_positions == targets
    
    def path_cost(self, c, state1, action, state2):
        """
        Calculates the cost of moving from state1 to state2 using the specified action.
        Simplified version that only checks if a box was moved and adds its weight.
        """
        worker_pos1, boxes1 = state1
        worker_pos2, boxes2 = state2
        
        # Base cost for worker movement
        cost = 1
        
        # Check if a box was moved by comparing the two states
        boxes1_pos = {pos for pos, _ in boxes1}
        boxes2_pos = {pos for pos, _ in boxes2}
        
        # Find the moved box position
        moved_box_pos = (boxes2_pos - boxes1_pos).pop() if (boxes2_pos - boxes1_pos) else None
        
        if moved_box_pos:
            # Find the weight of the moved box
            for pos, weight in boxes2:
                if pos == moved_box_pos:
                    cost += weight
                    break
                    
        return c + cost
    
    def can_move(self, state, action):
        """
        Determines whether the specified action can be legally performed in the current state.

        Args:
            state (tuple): The current state of the game, including worker and box positions.
            action (str): The action to evaluate (e.g., 'Up', 'Down', 'Left', 'Right').

        Returns:
            bool: True if the action can be legally performed, False otherwise.
        """
        dx, dy = directions[action] # Get the change in coordinates for the action
        worker_position, boxes = state # Unpack the state into worker position and boxes
        new_worker_pos = (worker_position[0] + dx, worker_position[1] + dy) # Calculate new worker position based on the action

        # Check if the new position is a wall
        if new_worker_pos in self.walls or not (0 <= new_worker_pos[0] < self.warehouse.ncols and 0 <= new_worker_pos[1] < self.warehouse.nrows):
            return False # Return False if the worker is moving into a wall

        box_positions = {box[0] for box in boxes} # Extract only positions
        # Check if the worker is pushing a box
        if new_worker_pos in box_positions:
            next_box_pos = (new_worker_pos[0] + dx, new_worker_pos[1] + dy) # Calculate the next box position
            # Check if the box can be moved to the next position
            if next_box_pos in self.walls or next_box_pos in box_positions or next_box_pos in self.taboo_cells:
                return False # Return False if the box cannot be moved
        # Return True if the worker can move: If none of the conditions fail, the move is legal
        return True

    @staticmethod
    def manhattan_distance(pos1, pos2):
        """
        Calculate the Manhattan distance between two points.
        
        Args:
        pos1, pos2: Tuples representing the (x, y) coordinates of the two points.
        
        Returns:
        The Manhattan distance between the two points.
        """
        # Calculate the Manhattan distance between the two points
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) *0.5
    
    def bfs_worker_to_box(self, worker_position, box_position):
        """
        Perform a breadth-first search (BFS) to find the shortest path from the worker to a specified box position,
        incorporating penalties for moving through taboo cells.

        Args:
            worker_position (tuple): The starting position of the worker.
            box_position (tuple): The target position of the box.

        Returns:
            int: The minimal distance from the worker to the box, adjusted for penalties, or float('inf') if no path exists.
        """
        penalty_for_taboo = 100 # Define penalty values for moving through taboo and potential taboo cells
        queue = deque([(worker_position, 0)])  # Start BFS with the worker position and distance 0
        visited = set() # Initialize a set to store visited cells
        visited.add(worker_position) # Add the worker position to the set of visited cells so that it is not revisited
        # Iterate through each cell in the queue
        while queue:
            (current_x, current_y), current_dist = queue.popleft() # Pop the current cell from the queue
            # Iterate through each direction
            for dx, dy in directions.values():  # Use globally defined directions
                next_x, next_y = current_x + dx, current_y + dy  # Calculate the next cell
                next_pos = (next_x, next_y) # Store the next position as a tuple
                # Check if the next position is the box position
                if next_pos == box_position[0]:
                    penalty = 0 # Initialize penalty for moving through taboo cells
                    # Check if the next position is a taboo cell
                    if next_pos in self.taboo_cells:
                        penalty += penalty_for_taboo # Add penalty for moving through a taboo cell
                    # Return the total distance from the worker to the box, adjusted for penalties
                    return current_dist + 1 + penalty 
                # Check if the next position is within the warehouse, not a wall, and not already visited
                if next_pos in visited or next_pos in self.walls or next_pos in {box[0] for box in self.boxes}:
                    continue # Skip the cell if it is a wall, already visited, or occupied by a box
                visited.add(next_pos) # Add the cell to the set of visited cells
                queue.append((next_pos, current_dist + 1)) # Add the cell to the queue with the updated distance
        # Ensure a default return of float('inf') if no path is found
        return float('inf')
    
    def calculate_worker_to_all_boxes_cost(self, state):
        """
        Calculates the minimal costs for the worker to reach each box from their current position.

        Args:
            state (tuple): Current state of the game, includes worker position and boxes.

        Returns:
            dict: A dictionary mapping each box's position to the minimal cost to reach it.
        """
        worker_position, boxes_positions = state # Unpack the state into worker position and boxes
        box_costs = {} # Initialize a dictionary to store the costs for each box
        # Iterate through each box position
        for box in boxes_positions:
            box_position = box[0]  # Extract position from tuple
            costs = [] # Initialize a list to store costs for each direction
            # Iterate through each direction
            for dx, dy in directions.values():
                push_side = (box_position[0] + dx, box_position[1] + dy) # Calculate the next cell
                # Check if the next cell is not a wall and not occupied by another box
                if push_side not in self.walls and all(push_side != other_box[0] for other_box in boxes_positions):
                    cost = self.bfs_worker_to_box(worker_position, push_side) # Calculate the cost to reach the next cell
                    # Add the cost to the list if it is not infinite
                    if cost != float('inf'):
                        costs.append((cost, push_side)) # Add the cost and position to the list
            # Add the minimal cost to reach the box to the dictionary
            if costs:
                box_costs[box_position] = min(costs, key=lambda x: x[0]) # Add the minimal cost to the dictionary
        # Return the dictionary mapping each box's position to the minimal cost to reach it
        return box_costs

    def calculate_box_to_target_cost(self, boxes_positions, targets):
        """
        Calculates the cost of moving each box to the nearest available target, considering penalties for
        placing boxes in taboo cells. Boxes are sorted by their weight to prioritize
        heavier boxes, potentially for strategic reasons like fewer moves for heavier boxes.

        Args:
            boxes_positions (list of tuples): A list where each tuple represents a box's position and its weight.
            targets (list of tuples): List of target positions.

        Returns:
            dict: A dictionary mapping each box's current position to its minimum cost to reach a target.
        """
        # Define penalties for boxes ending up in taboo cells
        penalty_for_taboo = 100  # High penalty for a box in a taboo cell

        sorted_boxes = sorted(boxes_positions, key=lambda box: box[1], reverse=True) # Sort by weight in descending order
        box_to_target_cost = {} # Initialize a dictionary to store costs for each box
        assigned_targets = set() # Initialize a set to store assigned targets
        # Iterate through each box position
        for box in sorted_boxes:
            box_position = box[0] # Extract the position
            box_weight = box[1] # Extract the weight
            min_cost = float('inf') # Initialize the minimum cost to infinity
            best_target = None # Initialize the best target as None

            # Sort available targets based on their Manhattan distance from the current box
            available_targets = sorted(targets, key=lambda t: SokobanPuzzle.manhattan_distance(box_position, t))
            # Evaluate each target for its potential as the best placement for the current box
            for target in available_targets:
                # Calculate the Manhattan distance from the box to the target
                if target not in assigned_targets:
                    distance = SokobanPuzzle.manhattan_distance(box_position, target) # Calculate the Manhattan distance from the box to the current target
                    cost = distance # Start with a base cost equal to the distance
                    nearest_distance = SokobanPuzzle.manhattan_distance(box_position, available_targets[0]) # Fetch the distance to the nearest target for comparison
                    # Apply a reward or penalty based on the distance to the nearest target
                    if distance == nearest_distance:
                        # Reward by reducing the cost for boxes placed on the nearest target
                        cost -= 50 * box_weight  # Negative reward reduces the cost
                    else:
                        penalty = (distance - nearest_distance) * box_weight # Calculate the penalty for moving away from the nearest target
                        cost += penalty # Add the penalty to the cost
                    # Add penalties if the box position is on a taboo cell
                    if box_position in self.taboo_cells:
                        cost += penalty_for_taboo # Add penalty for placing a box in a taboo cell
                    # Update the minimum cost and best target if the current target is better
                    if cost < min_cost:
                        min_cost = cost # Update the minimum cost
                        best_target = target # Update the best target
            # Update the dictionary with the minimum cost for the current box
            if best_target:
                assigned_targets.add(best_target) # Add the best target to the set of assigned targets
                box_to_target_cost[box_position] = min_cost # Update the dictionary with the minimum cost
            else:
                box_to_target_cost[box_position] = float('inf') # Update the dictionary with infinity if no target is found
        # Return the dictionary mapping each box's current position to its minimum cost to reach a target
        return box_to_target_cost
    
    def calculate_optimal_assignment_cost(self, boxes_positions):
        """
        Calculates the minimal total cost for optimally assigning each box to a target. The cost is based on the distance
        the box needs to be moved, weighted by the box's weight, and adjusted for being closer to or farther from the 
        nearest target.

        Args:
            boxes_positions (list of tuples): Each tuple contains a box's position and its weight.
        
        Returns:
            float: The minimal cost of assigning all boxes to all targets.
        """
        min_cost = float('inf') # Initialize the minimal cost to infinity to ensure any lower cost found is recorded
        sorted_boxes = sorted(boxes_positions, key=lambda x: x[1], reverse=True)  # Sort boxes by their weights in descending order to prioritize heavier boxes in assignment
        # Generate all permutations of the target positions to evaluate all possible assignments
        for permutation in itertools.permutations(self.goal):
            current_cost = 0 # Start with a current cost of 0 for this permutation of assignments
            already_assigned_targets = set() # Track assigned targets to avoid assigning multiple boxes to the same target
            # Iterate through each box and target to calculate the cost of the current assignment
            for box, target in zip(sorted_boxes, permutation):
                box_position = box[0] # Extract the box position: Position of the box
                weight = box[1] # Extract the box weight : Weight of the box
                distance = SokobanPuzzle.manhattan_distance(box_position, target) # Calculate the Manhattan distance from the box to the target
                closest_target = min(self.goal, key=lambda t: SokobanPuzzle.manhattan_distance(box_position, t)) # Find the closest target to the box position to determine if the assignment is optimal
                closest_distance = SokobanPuzzle.manhattan_distance(box_position, closest_target) # Calculate the distance to the closest target
                # If the target is not already assigned, calculate the cost or reward
                if target not in already_assigned_targets:
                    # Apply a reward (negative cost) for assigning the box to the closest target
                    if target == closest_target:
                        reward = -50 * weight # Negative reward reduces the cost
                    else:
                        penalty = (distance - closest_distance) * weight # Penalize assignments that are not to the nearest target more heavily for heavier boxes
                        current_cost += distance + penalty # Add the distance and penalty to the current cost
                    already_assigned_targets.add(target) # Add the target to the set of already assigned targets
                else:
                    current_cost += distance * 10 # If a target is already assigned, heavily penalize reassignment
            min_cost = min(min_cost, current_cost) # Update the minimal cost found across all permutations
        # Return the minimal cost of assigning all boxes to all targets
        return min_cost
        
    def heuristic(self, node):
        """
        Calculates a heuristic value for the given state of the Sokoban puzzle.
        Uses a simpler and more efficient heuristic that focuses on:
        1. Distance of boxes to their nearest targets
        2. Worker's distance to boxes
        3. Penalties for taboo cells
        """
        state = node.state
        worker_pos, boxes = state
        
        # Calculate total distance of boxes to their nearest targets
        total_box_target_distance = 0
        for box_pos, weight in boxes:
            # Find nearest unassigned target
            min_dist = float('inf')
            for target in self.goal:
                dist = self.manhattan_distance(box_pos, target)
                if dist < min_dist:
                    min_dist = dist
            total_box_target_distance += min_dist * weight
            
        # Calculate worker's distance to nearest box
        min_worker_box_dist = float('inf')
        for box_pos, _ in boxes:
            dist = self.manhattan_distance(worker_pos, box_pos)
            if dist < min_worker_box_dist:
                min_worker_box_dist = dist
                
        # Calculate taboo cell penalties
        taboo_penalty = sum(100 for box_pos, _ in boxes if box_pos in self.taboo_cells)
        
        # Combine components with appropriate weights
        return total_box_target_distance + min_worker_box_dist + taboo_penalty

    def penalty_for_box(self, box_position):
        """
        Calculates a penalty for a box based on its location relative to taboo cells.

        Args:
            box_position (tuple): The position of the box.

        Returns:
            int: A penalty score for the box's position.
        """
        penalty = 0 # Initialize the penalty score
        # Apply high penalty for boxes placed in taboo cells
        if box_position in self.taboo_cells:
            penalty += 100  # High penalty for pushing a box to a taboo cell
        # Return the total penalty for the box's position
        return penalty
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def check_elem_action_seq(warehouse, action_seq):
    '''
    
    Determine if the sequence of actions listed in 'action_seq' is legal or not.
    
    Important notes:
      - a legal sequence of actions does not necessarily solve the puzzle.
      - an action is legal even if it pushes a box onto a taboo cell.
        
    @param warehouse: a valid Warehouse object

    @param action_seq: a sequence of legal actions.
           For example, ['Left', 'Down', Down','Right', 'Up', 'Down']
           
    @return
        The string 'Impossible', if one of the action was not valid.
           For example, if the agent tries to push two boxes at the same time,
                        or push a box into a wall.
        Otherwise, if all actions were successful, return                 
               A string representing the state of the puzzle after applying
               the sequence of actions.  This must be the same string as the
               string returned by the method  Warehouse.__str__()
    '''
    
    ##         "INSERT YOUR CODE HERE"
    
    # Helper function to move in a direction
    def move(direction, pos):
        dx, dy = directions[direction]   # Get the change in coordinates for the action
        # Calculate the new position after moving in the specified direction
        return pos[0] + dx, pos[1] + dy

    # Copy warehouse elements to avoid modifying the original object
    worker = warehouse.worker # Get the worker position
    boxes = set(warehouse.boxes) # Get the set of box positions
    walls = warehouse.walls # Get the set of wall positions
    # Iterate through each action in the sequence
    for action in action_seq:
        new_worker_pos = move(action, worker) # Calculate the new worker position after moving in the specified direction
        # Check if the worker moves into a wall
        if new_worker_pos in walls:
            return "Impossible" # Return 'Impossible' if the worker moves into a wall
        # Check if the worker moves a box
        if new_worker_pos in boxes:
            new_box_pos = move(action, new_worker_pos) # Calculate the new box position after moving in the specified direction
            # Check if the box is pushed into a wall or another box
            if new_box_pos in walls or new_box_pos in boxes:
                return "Impossible" # Return 'Impossible' if the box is pushed into a wall or another box
            # Update box position
            boxes.remove(new_worker_pos) # Remove the old box position
            boxes.add(new_box_pos) # Add the new box position
        # Update worker position
        worker = new_worker_pos # Update the worker position after moving

    # After processing all actions, generate and return the resulting warehouse state as a string
    final_state = warehouse.copy(worker=worker, boxes=list(boxes)) # Construct the new warehouse state
    # Return the string representation of the final state
    return str(final_state)
    
def check_each_action_and_move(warehouse, action_seq):
    '''
    Same purpose as check_action_seq function
    NB: It does not check if it pushes a box onto a taboo cell.
    
    @param warehouse: a Warehouse object
    @param action_seq: a list of actions
    
    @return
        a altered warehouse
    '''

    def attempt_move(worker, direction):
        '''Return the new position of the worker after moving in the given direction.'''
        # Calculate the new position after moving in the specified direction
        return worker[0] + directions[direction][0], worker[1] + directions[direction][1]
    
    def is_move_valid(position, boxes, walls):
        '''Check if the move is valid, not blocked by walls or boxes.'''
        # Check if the position is not a wall or occupied by a box
        return position not in walls and position not in boxes
    
    worker = warehouse.worker # Get the worker position
    boxes = set(warehouse.boxes) # Get the set of box positions
    walls = set(warehouse.walls) # Get the set of wall positions
    # Iterate through each action in the sequence
    for action in action_seq:
        new_worker_pos = attempt_move(worker, action) # Calculate the new worker position after moving in the specified direction
        # Check if the worker moves into a wall
        if new_worker_pos in boxes:
            # Attempt to push the box
            new_box_pos = attempt_move(new_worker_pos, action) # Calculate the new box position after moving in the specified direction
            if not is_move_valid(new_box_pos, boxes, walls): # Check if the box move is valid
                return "Impossible"
            boxes.remove(new_worker_pos)  # Remove the old box position
            boxes.add(new_box_pos)  # Add the new box position
        # Check if the worker moves into a wall
        elif not is_move_valid(new_worker_pos, boxes, walls): 
            return "Impossible" # Return 'Impossible' if the worker moves into a wall
        
        worker = new_worker_pos  # Update the worker's position

    # Construct the new warehouse state from the final positions of worker and boxes
    final_warehouse = warehouse.copy(worker=list(worker), boxes=list(boxes))
    # Return the string representation of the final state
    return str(final_warehouse)

def isNot_boxes_next_move(x, y, boxes):
    '''Check if the next move does not have a box.'''
    # Check if the position is not occupied by a box
    return (x, y) not in boxes 

def isNot_walls_next_move(x, y, walls):
    '''Check if the next move does not have a wall.'''
    # Check if the position is not a wall
    return (x, y) not in walls

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def solve_weighted_sokoban(warehouse):
    '''
    This function analyses the given warehouse.
    It returns the two items. The first item is an action sequence solution. 
    The second item is the total cost of this action sequence.

    @param 
     warehouse: a valid Warehouse object

    @return
    
        If puzzle cannot be solved 
            return 'Impossible', None
        
        If a solution was found, 
            return S, C 
            where S is a list of actions that solves
            the given puzzle coded with 'Left', 'Right', 'Up', 'Down'
            For example, ['Left', 'Down', Down','Right', 'Up', 'Down']
            If the puzzle is already in a goal state, simply return []
            C is the total cost of the action sequence C

    '''
    # Initialize the puzzle
    puzzle = SokobanPuzzle(warehouse)

    # Check if the initial state already meets the goal
    if puzzle.goal_test(puzzle.initial):
        return [], 0  # No actions needed, cost is zero

    # Use A* search algorithm to find the solution path with the heuristic function defined in SokobanPuzzle
    solution_node = astar_graph_search(puzzle, puzzle.heuristic)
    # Check if a solution was found
    if solution_node is None:
        return 'Impossible', None # Return 'Impossible' if no solution was found
    
    actions = solution_node.solution()  # This gets the sequence of actions from the initial state to the goal
    cost = solution_node.path_cost # This gets the total cost of the solution path
    # Return the sequence of actions and the total cost of the solution path 
    if not actions:
        return 'Impossible', None # Return 'Impossible' if no solution was found
    # Return the sequence of actions and the total cost of the solution path
    return actions, cost

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
'''
Other testing code:
Place the code in sanity_check.py, call it in if __name__ == "__main__":
    list_boxes_by_weight()
    
def list_boxes_by_weight():
    wh = Warehouse()
    wh.load_warehouse(file_path)
    
    # Create a list of boxes sorted by their weight (heaviest first)
    sorted_boxes = sorted(zip(wh.boxes, wh.weights), key=lambda x: x[1], reverse=True)

    box_to_target = {}  # To store the assigned target for each box
    assigned_targets = set()  # To keep track of targets already assigned

    # Assign each box to the nearest available target
    for box, weight in sorted_boxes:
        nearest_target = None
        nearest_distance = float('inf')

        for target in wh.targets:
            if target not in assigned_targets:
                distance = abs(box[0] - target[0]) + abs(box[1] - target[1])
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_target = target

        if nearest_target:
            box_to_target[box] = (nearest_target, nearest_distance)
            assigned_targets.add(nearest_target)  # Mark this target as assigned

    # Print the assignments
    print("Box assignments from heaviest to lightest:")
    for box, weight in sorted_boxes:
        if box in box_to_target:
            target, distance = box_to_target[box]
            print(f"Box at {box} with weight {weight}: Assigned target at {target}, Distance: {distance}")
        else:
            print(f"Box at {box} with weight {weight}: No available target")

if __name__ == "__main__":
    list_boxes_by_weight()
    
'''