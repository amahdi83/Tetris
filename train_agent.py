import random
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from collections import deque
import os




class ExperienceBuffer:
    """Replay memory to store experiences"""
    def __init__(self, buffer_size=20000):
        self.buffer = deque(maxlen=buffer_size)

    def add(self, experience):
        self.buffer.append(experience)

    def sample(self, size):
        return random.sample(self.buffer, min(len(self.buffer), size))
    
    
    
class DeepQNetwork(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DeepQNetwork, self).__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, 32)
        self.fc4 = nn.Linear(32, output_dim)
        
        self._create_weights()

    def _create_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                nn.init.constant_(m.bias, 0)


    def forward(self, x):
        device = next(self.parameters()).device  # Get model’s device
        x = x.to(device)  # Move input to the same device as the model
        
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = self.fc4(x)
        return x 
    


class QNetwork(nn.Module):
    """Deep Q-Learning Network"""
    def __init__(self, state_size=9, discount=1, epsilon=1, epsilon_min=0.0001, epsilon_decay=0.99995, lr=0.001):
        super(QNetwork, self).__init__()
        self.state_size = state_size
        self.discount = discount
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        
        self.model = DeepQNetwork(input_dim=self.state_size, output_dim=1)

        self.optimizer = optim.Adam(self.parameters(), lr=lr)
        self.criterion = nn.MSELoss()
        self.experiences = ExperienceBuffer()
        
        self.WEIGHT_PATH = os.path.join(os.path.dirname(__file__), 'weights.pth')

    def forward(self, x):
        """Forward pass"""
        return self.model(x)

    def act(self, possible_states):
        """Select an action using an ε-greedy policy"""
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(possible_states)  # Explore

        max_rating = None
        best_state = None

        states_tensor = torch.tensor([state for action, state in possible_states], dtype=torch.float32)
        # ratings = self.forward(states_tensor).detach().numpy()
        ratings = self.forward(states_tensor).detach().cpu().numpy()

        for i, (action, state) in enumerate(possible_states):
            rating = ratings[i]
            if max_rating is None or rating > max_rating:
                max_rating = rating
                best_state = (action, state)

        return best_state  # Exploit best known state

    # def train(self, env, episodes):
    def train(self, env, episodes=1000):
        """Train the network for a given number of episodes"""
        rewards = []
        scores = []
        steps = 0

        for episode in range(episodes):
            obs = env.reset()
            # previous_state = env.get_info([])
            previous_state = env.get_info([], env.board)

            done = False
            total_reward = 0

            while not done:
                action, state = self.act(obs)
                obs, reward, done, info = env.step(action, render=True)
                self.experiences.add((previous_state, reward, state, done))
                previous_state = state
                steps += 1
                total_reward += reward

            rewards.append(total_reward)
            scores.append(env.SCORE)
            
            print(f"Epoch {episode}, Epsilon: {self.epsilon:.4f}, Reward: {total_reward:.1f}, Score: {env.SCORE}, Lines Cleared: {env.lines_cleared}")

            self.learn()

        return [steps, rewards, scores]




    def learn(self, batch_size=512):
        if len(self.experiences.buffer) < batch_size:
            return
    
        batch = self.experiences.sample(batch_size)
        
    
        states, rewards, next_states, dones = zip(*batch)
    
        states = torch.tensor(states, dtype=torch.float32).to("mps")
        next_states = torch.tensor(next_states, dtype=torch.float32).to("mps")
        rewards = torch.tensor(rewards, dtype=torch.float32).to("mps")
        dones = torch.tensor(dones, dtype=torch.bool).to("mps")
    
        q_values = self.forward(next_states).detach().squeeze()
        targets = rewards + self.discount * q_values * (~dones)
    
        self.optimizer.zero_grad()
        predictions = self.forward(states).squeeze()
        loss = self.criterion(predictions, targets)
        loss.backward()
        self.optimizer.step()
    
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)


    def save(self):
        """Save the model"""
        torch.save(self.state_dict(), self.WEIGHT_PATH)

    
    def load(self):
        """Load the model correctly without calling train()."""
        if os.path.exists(self.WEIGHT_PATH):
            try:
                self.load_state_dict(torch.load(self.WEIGHT_PATH, map_location=torch.device("mps")), strict=False)
                self.eval()  # Put model in evaluation mode (inference mode)
                print("[INFO] Model loaded successfully!")
            except Exception as e:
                print(f"[ERROR] Failed to load model: {e}")