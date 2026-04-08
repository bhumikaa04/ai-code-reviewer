import random
from collections import defaultdict

class RLAgent:
    def __init__(self, actions):
        self.actions = actions
        self.q_table = defaultdict(lambda: [0.0] * len(actions))

        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 1.0   # start high for exploration

    def choose_action(self, state):
        # Exploration
        if random.random() < self.epsilon:
            return random.randint(0, len(self.actions) - 1)

        # Exploitation (FIXED: no bias)
        q_values = self.q_table[state]
        max_q = max(q_values)

        best_actions = [i for i, q in enumerate(q_values) if q == max_q]
        return random.choice(best_actions)

    def update(self, state, action, reward, next_state):
        best_next = max(self.q_table[next_state])
        self.q_table[state][action] += self.alpha * (
            reward + self.gamma * best_next - self.q_table[state][action]
        )

    def decay_epsilon(self):
        self.epsilon *= 0.995
        self.epsilon = max(0.05, self.epsilon)