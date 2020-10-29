import numpy as np
import random

# Globals
LEARNING_RATE = 1
DISCOUNT = 1
state_size = 0
action_size = 0
epsilon = 0.2  # up to 1
gamma = 0.8  # up to 0.99
lr = 0  # up to 1

# Initialize q-table values to 0
Q = np.zeros((state_size, action_size))

# action = 0 = for

Q[state, action] = Q[state, action] + lr * (reward + gamma * np.max(Q[new_state, :]) — Q[state, action])

# Set the percent you want to explore
if random.uniform(0, 1) < epsilon:
    """
    Explore: select a random action
    """
else:
    """
    Exploit: select the action with max value (future reward)
    """
