import pygame
from train_agent import QNetwork
from tetris_env import TetrisEnv
from tetris import Tetris




def run_tetris():
    game = Tetris()
    game.fall_time = 500
    game.run()

def train_tetris():
    env = TetrisEnv()
    q_network = QNetwork(state_size=9).to("mps")
    
    episodes = 10000
    q_network.train(env, episodes)

    # Save the trained model
    q_network.save()
    

def test_tetris():
    # Initialize Tetris environment
    env = TetrisEnv()
    
    # Load trained model
    network = QNetwork(discount=1, epsilon=0, epsilon_min=0, epsilon_decay=0)
    network.load()  # Ensure this method correctly loads `state_dict()`
    
    obs = env.reset()
    running = True
    display = True

    while running:
        # Get action using trained model
        possible_states = env.get_possible_states()
        if not possible_states:
            break  # No valid moves, end game
        
        action, _ = network.act(possible_states)

        # Step environment with selected action
        obs, reward, done, _ = env.step(action, render=display)

        # Handle user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    display = not display  # Toggle rendering

        # Restart game if it's over
        if done:
            obs = env.reset()

    env.close()
    
    
    
    
if __name__ == "__main__":
    
    mode = "test"
    
    
    if mode == "play": # play the game manually
        run_tetris()
        
    elif mode == "train": # train an AI model
        train_tetris()
        
    elif mode == "test":
        test_tetris() # AI plays the game