import math 
import heapq
import random

from config.settings import * 

class Node:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g_cost = 0
        self.h_cost = 0
        self.f_cost = 0

    def __lt__(self, other):
        return self.f_cost < other.f_cost

def a_star_search(start, goal, snake_body, grid_width, grid_height):
    open_list = []
    closed_set = set()
    start_node = Node(start)
    goal_node = Node(goal)

    heapq.heappush(open_list, start_node)
    if VERBOSE:
        print(f"Starting A* search from {start} to {goal}")

    while open_list:
        current_node = heapq.heappop(open_list)
        closed_set.add(current_node.position)

        # Check if we reached the goal
        if current_node.position == goal_node.position:
            path = []
            while current_node is not None:
                path.append(current_node.position)
                current_node = current_node.parent
            if VERBOSE:
                print(f"Path found: {path[::-1]}")
            return path[::-1]  # Return reversed path

        # Generate neighbors (UP, DOWN, LEFT, RIGHT)
        neighbors = [
            (current_node.position[0] + 0, current_node.position[1] - 1),  # UP
            (current_node.position[0] + 0, current_node.position[1] + 1),  # DOWN
            (current_node.position[0] - 1, current_node.position[1] + 0),  # LEFT
            (current_node.position[0] + 1, current_node.position[1] + 0),  # RIGHT
        ]

        for next_position in neighbors:
            x, y = next_position

            # Check if within bounds
            if x < 0 or x >= grid_width or y < 0 or y >= grid_height:
                continue

            # Check if on snake's body
            if next_position in snake_body:
                continue

            # Create neighbor node
            neighbor = Node(next_position, current_node)
            if neighbor.position in closed_set:
                continue

            # Calculate costs
            neighbor.g_cost = current_node.g_cost + 1
            neighbor.h_cost = abs(neighbor.position[0] - goal_node.position[0]) + abs(neighbor.position[1] - goal_node.position[1])
            neighbor.f_cost = neighbor.g_cost + neighbor.h_cost

            # Check if neighbor is in open list with a lower f_cost
            if any(open_node.position == neighbor.position and open_node.f_cost <= neighbor.f_cost for open_node in open_list):
                continue

            heapq.heappush(open_list, neighbor)

    if VERBOSE:
        print("No path found")
    return []  # Return empty path if no path is found

"""
Move the snake using A* algorithm towards the food.
"""
def a_star_move(snake, food, board):

    # Adjust start and goal to align with the grid
    start = (snake.head_position()[0] // TILE_SIZE, snake.head_position()[1] // TILE_SIZE)
    goal = (food.position[0] // TILE_SIZE, food.position[1] // TILE_SIZE)

    grid_width = board.grid_width
    grid_height = board.grid_height

    # Convert snake body positions to grid coordinates
    snake_body = [(segment[0] // TILE_SIZE, segment[1] // TILE_SIZE) for segment in snake.body]

    path = a_star_search(start, goal, snake_body, grid_width, grid_height)

    if len(path) > 1:
        next_position = path[1]
        head_x, head_y = snake.head_position()
        next_x, next_y = next_position[0] * TILE_SIZE, next_position[1] * TILE_SIZE  # Convert back to pixel coordinates

        if next_y < head_y:
            snake.change_direction("UP")
        elif next_y > head_y:
            snake.change_direction("DOWN")
        elif next_x < head_x:
            snake.change_direction("LEFT")
        elif next_x > head_x:
            snake.change_direction("RIGHT")
    else:
        # No path found, try to move randomly to stay alive
        stay_alive(snake, board)

    # Move the snake
    snake.move()

"""
Attempt to keep the snake alive by making a safe random move.
"""
def stay_alive(snake, board):

    possible_moves = [
        ((0, -1), "UP"),
        ((0, 1), "DOWN"),
        ((-1, 0), "LEFT"),
        ((1, 0), "RIGHT")
    ]

    head_x, head_y = snake.head_position()
    snake_body = [(segment[0] // TILE_SIZE, segment[1] // TILE_SIZE) for segment in snake.body]
    safe_moves = []

    # Filter out moves that lead to collisions
    for move, direction in possible_moves:
        next_x = (head_x // TILE_SIZE) + move[0]
        next_y = (head_y // TILE_SIZE) + move[1]

        # Check if within bounds and not colliding with itself
        if 0 <= next_x < board.grid_width and 0 <= next_y < board.grid_height:
            if (next_x, next_y) not in snake_body:
                safe_moves.append(direction)

    # If there are safe moves, pick one randomly
    if safe_moves:
        snake.change_direction(random.choice(safe_moves))
    else:
        # If no safe moves, do nothing (snake will stay in place, likely to die)
        if VERBOSE:
            print("No safe moves available, snake is trapped.")

@property
def a_star_average_score(self):
    """Calculate the average score of all A* runs."""
    if self.a_star_runs > 0:
        return self.a_star_total_score / self.a_star_runs
    return 0