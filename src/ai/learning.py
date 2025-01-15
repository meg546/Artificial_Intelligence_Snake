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
    def __init__(
                 self, 
                 state_space_size, 
                 action_space_size, 
                 learning_rate=0.002, 
                 gamma=0.9, 
                 max_memory=100000, 
                 batch_size=1000,
                 epsilon_start=0, 
                 epsilon_end=0,
                ):
        
        self.state_space_size = state_space_size
        self.action_space_size = action_space_size
        self.gamma = gamma
        self.memory = deque(maxlen=max_memory)
        self.batch_size = batch_size
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")

        # Neural Network
        self.model = DeepQNetwork(state_space_size, 256, action_space_size).to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        self.loss_fn = nn.MSELoss()

        self.target_model = DeepQNetwork(state_space_size, 256, action_space_size).to(self.device)
        self.target_model.load_state_dict(self.model.state_dict())  # Copy weights from the main model
        self.target_update_interval = 1000  # Update target model every 1000 steps
        self.n_games = 0


        # Epsilon parameters
        self.epsilon = epsilon_start
        self.epsilon_min = epsilon_end

    def decay_epsilon(self):
        epsilon_decay_rate = (self.epsilon - self.epsilon_min) / 7500  # Adjust # to the number of runs desired
        self.epsilon = max(self.epsilon - epsilon_decay_rate, self.epsilon_min)

    def choose_action(self, state, epsilon=None):
        if epsilon is None:
            epsilon = self.epsilon  # Use the model's epsilon if not provided

        if random.random() < epsilon:
            return random.randint(0, self.action_space_size - 1)  # Explore
        state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0).to(self.device)
        q_values = self.model(state_tensor)
        return torch.argmax(q_values).item()  # Exploit

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_step(self, state, action, reward, next_state, done):
        # Convert to tensors
        state = torch.tensor(state, dtype=torch.float).to(self.device)
        next_state = torch.tensor(next_state, dtype=torch.float).to(self.device)
        action = torch.tensor(action, dtype=torch.long).to(self.device)
        reward = torch.tensor(reward, dtype=torch.float).to(self.device)
        done = torch.tensor(done).to(self.device)

        if len(state.shape) == 1:  # Handle single state case
            state = state.unsqueeze(0)
            next_state = next_state.unsqueeze(0)
            action = action.unsqueeze(0)
            reward = reward.unsqueeze(0)
            done = done.unsqueeze(0)

        # Predict Q values
        q_values = self.model(state).gather(1, action.unsqueeze(1)).squeeze(1)

        # Calculate targets
        with torch.no_grad():
            max_next_q_values = self.target_model(next_state).max(1)[0]
            target = reward + self.gamma * max_next_q_values * (~done)

        # Backpropagation
        loss = self.loss_fn(q_values, target)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def save_model(self, filename="model.pth"):
        torch.save(self.model.state_dict(), filename)

    def load_model(self, filename="model.pth"):
        if os.path.exists(filename):
            self.model.load_state_dict(torch.load(filename, map_location=torch.device('cpu')))
            self.model.eval()  # Switch to evaluation mode
            print("Model loaded successfully.")
        else:
            print("No saved model found. Starting fresh.")

    def get_state(self, snake, food, board):
        head_x, head_y = snake.head_position()
        fruit_x, fruit_y = food.position

        # Danger detection
        danger_straight = snake.will_collide(snake.direction, board.width, board.height, board.walls)
        danger_left = snake.will_collide(snake.turn_left(), board.width, board.height, board.walls)
        danger_right = snake.will_collide(snake.turn_right(), board.width, board.height, board.walls)

        # Current movement direction
        dir_up = int(snake.direction == "UP")
        dir_down = int(snake.direction == "DOWN")
        dir_left = int(snake.direction == "LEFT")
        dir_right = int(snake.direction == "RIGHT")

        # Food relative position
        food_left = int(fruit_x < head_x)
        food_right = int(fruit_x > head_x)
        food_up = int(fruit_y < head_y)
        food_down = int(fruit_y > head_y)

        # Combine all features into a state vector
        state = [
            danger_straight, danger_left, danger_right,
            dir_up, dir_down, dir_left, dir_right,
            food_left, food_right, food_up, food_down,
        ]

        return np.array(state, dtype=int)

    def get_reward(self, snake, food, board):
        fruit_x, fruit_y = food.position
        next_head_x, next_head_y = snake.get_next_head_position()

        dist_to_food_before = abs(snake.head_position()[0] - fruit_x) + abs(snake.head_position()[1] - fruit_y)
        dist_to_food_after = abs(next_head_x - fruit_x) + abs(next_head_y - fruit_y)

        if not board.is_within_bounds((next_head_x, next_head_y)) or snake.has_collision(board):
            return -10  # Large penalty for dying
        elif (next_head_x, next_head_y) == (fruit_x, fruit_y):
            return 20  # Large reward for eating food
        elif dist_to_food_after < dist_to_food_before:
            return 2  # Small reward for getting closer to food
        else:
            return -1  # Small penalty for moving farther away
        
    def update_target_model(self):
        if self.n_games % 10 == 0:  # Update every 10 games
            self.target_model.load_state_dict(self.model.state_dict())
            print("Target model updated.")




