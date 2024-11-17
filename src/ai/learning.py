import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np
from collections import deque
import os


class DeepQNetwork(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(DeepQNetwork, self).__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = torch.relu(self.linear1(x))
        x = self.linear2(x)
        return x

class DeepQLearningModel:
    def __init__(self, state_space_size, action_space_size, learning_rate=0.001, gamma=0.9, max_memory=100000, batch_size=64):
        self.state_space_size = state_space_size
        self.action_space_size = action_space_size
        self.gamma = gamma
        self.memory = deque(maxlen=max_memory)
        self.batch_size = batch_size
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Neural Network
        self.model = DeepQNetwork(state_space_size, 256, action_space_size).to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        self.loss_fn = nn.MSELoss()

    def choose_action(self, state, epsilon=None):
        """
        Choose an action using epsilon-greedy policy.
        - state: Current state of the game.
        - epsilon: Exploration rate (probability of random action).
        """
        if epsilon is None:
            epsilon = self.epsilon  # Use the model's epsilon if not provided

        if random.random() < epsilon:
            return random.randint(0, self.action_space_size - 1)  # Explore
        state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0).to(self.device)
        q_values = self.model(state_tensor)
        return torch.argmax(q_values).item()  # Exploit

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_short_memory(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float).to(self.device)
        next_state = torch.tensor(next_state, dtype=torch.float).to(self.device)
        action = torch.tensor([action]).to(self.device)
        reward = torch.tensor([reward]).to(self.device)
        done = torch.tensor([done]).to(self.device)

        # Q-learning formula
        q_update = reward
        if not done:
            with torch.no_grad():
                q_update = reward + self.gamma * torch.max(self.model(next_state))

        q_values = self.model(state)
        q_values[action] = q_update

        # Calculate loss and backpropagate
        self.optimizer.zero_grad()
        loss = self.loss_fn(q_values, self.model(state))
        loss.backward()
        self.optimizer.step()

    def train_long_memory(self):
        if len(self.memory) < self.batch_size:
            return

        mini_batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*mini_batch)

        states = torch.tensor(states, dtype=torch.float).to(self.device)
        next_states = torch.tensor(next_states, dtype=torch.float).to(self.device)
        actions = torch.tensor(actions).to(self.device)
        rewards = torch.tensor(rewards, dtype=torch.float).to(self.device)
        dones = torch.tensor(dones, dtype=torch.bool).to(self.device)

        # Q-learning formula
        q_values = self.model(states)
        with torch.no_grad():
            q_next_values = self.model(next_states)
            q_updates = rewards + (self.gamma * torch.max(q_next_values, dim=1).values * (~dones))

        # Update Q-values for chosen actions
        q_values[range(self.batch_size), actions] = q_updates

        # Calculate loss and backpropagate
        self.optimizer.zero_grad()
        loss = self.loss_fn(q_values, self.model(states))
        loss.backward()
        self.optimizer.step()

    def save_model(self, filename="model.pth"):
        torch.save(self.model.state_dict(), filename)

    def load_model(self, filename="model.pth"):
        if os.path.exists(filename):
            self.model.load_state_dict(torch.load(filename))
            self.model.eval()  # Switch to evaluation mode
            print("Model loaded successfully.")
        else:
            print("No saved model found. Starting fresh.")


    def get_state(self, snake, food, board):
        """
        Generate a state representation for the Deep Q-Learning model.
        Includes:
        - Relative position of food
        - Current direction of the snake
        - Proximity to walls
        - Proximity to the snake's body
        """
        head_x, head_y = snake.head_position()
        fruit_x, fruit_y = food.position

        # Relative position of food (normalized)
        rel_food_x = (fruit_x - head_x) / board.width
        rel_food_y = (fruit_y - head_y) / board.height

        # Current movement direction of the snake
        dir_up = int(snake.direction == "UP")
        dir_down = int(snake.direction == "DOWN")
        dir_left = int(snake.direction == "LEFT")
        dir_right = int(snake.direction == "RIGHT")

        # Distances to walls (normalized)
        dist_wall_up = head_y / board.height
        dist_wall_down = (board.height - head_y) / board.height
        dist_wall_left = head_x / board.width
        dist_wall_right = (board.width - head_x) / board.width

        # Detect body collisions in each direction
        body_up = body_down = body_left = body_right = 0
        for segment in snake.body:
            if segment[0] == head_x and segment[1] < head_y:
                body_up = 1
            elif segment[0] == head_x and segment[1] > head_y:
                body_down = 1
            elif segment[1] == head_y and segment[0] < head_x:
                body_left = 1
            elif segment[1] == head_y and segment[0] > head_x:
                body_right = 1

        # Combine all features into a state vector
        state = [
            rel_food_x, rel_food_y,       # Food position
            dir_up, dir_down, dir_left, dir_right,  # Snake direction
            dist_wall_up, dist_wall_down, dist_wall_left, dist_wall_right,  # Wall distances
            body_up, body_down, body_left, body_right  # Body proximity
        ]

        return state

    def get_reward(self, snake, food, board):
        head_x, head_y = snake.head_position()
        fruit_x, fruit_y = food.position

        # Manhattan distance to food
        distance_before = abs(head_x - fruit_x) + abs(head_y - fruit_y)
        next_head_x, next_head_y = snake.get_next_head_position()
        distance_after = abs(next_head_x - fruit_x) + abs(next_head_y - fruit_y)

        # Reward system
        if not board.is_within_bounds((next_head_x, next_head_y)) or snake.has_collision():
            return -10  # Large penalty for dying
        elif (next_head_x, next_head_y) == (fruit_x, fruit_y):
            return 10  # Large reward for eating food
        else:
            return 0  # no reward
