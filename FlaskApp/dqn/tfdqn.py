import gym
import numpy as np
import tensorflow as tf

# Define the hyperparameters
lr = 0.001
gamma = 0.99
epsilon = 1.0
epsilon_min = 0.01
epsilon_decay = 0.995
batch_size = 32
memory_size = 10000

# Create the replay buffer
class ReplayBuffer:
    def __init__(self, memory_size):
        self.memory = []
        self.memory_size = memory_size

    def add(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
        if len(self.memory) > self.memory_size:
            self.memory.pop(0)

    def sample(self, batch_size):
        batch = np.random.choice(len(self.memory), batch_size, replace=False)
        state_batch = np.array([self.memory[i][0] for i in batch])
        action_batch = np.array([self.memory[i][1] for i in batch])
        reward_batch = np.array([self.memory[i][2] for i in batch])
        next_state_batch = np.array([self.memory[i][3] for i in batch])
        done_batch = np.array([self.memory[i][4] for i in batch])
        return state_batch, action_batch, reward_batch, next_state_batch, done_batch

# Define the deep Q-network
class DQN(tf.keras.Model):
    def __init__(self, n_states, n_actions):
        super(DQN, self).__init__()
        self.dense1 = tf.keras.layers.Dense(128, activation='relu')
        self.dense2 = tf.keras.layers.Dense(128, activation='relu')
        self.dense3 = tf.keras.layers.Dense(n_actions)

    def call(self, inputs):
        x = self.dense1(inputs)
        x = self.dense2(x)
        x = self.dense3(x)
        return x

# Initialize the environment and the replay buffer
env = gym.make('CartPole-v1')
replay_buffer = ReplayBuffer(memory_size)

# Initialize the deep Q-network and the optimizer
dqn = DQN(env.observation_space.shape[0], env.action_space.n)
optimizer = tf.keras.optimizers.Adam(lr)

# Train the deep Q-network
for episode in range(1000):
    state = env.reset()
    state = state[0]
    done = False
    total_reward = 0
    while not done:
        # Choose an action using epsilon-greedy policy
        if np.random.rand() < epsilon:
            action = env.action_space.sample()
        else:
            action = tf.argmax(dqn(np.array([state]))[0]).numpy()

        # Take a step in the environment and add the experience to the replay buffer
        next_state, reward, done, _ = env.step(action)
        next_state = next_state[0]
        replay_buffer.add(state, action, reward, next_state, done)
        total_reward += reward
        state = next_state

        # Update the deep Q-network
        if len(replay_buffer.memory) > batch_size:
            state_batch, action_batch, reward_batch, next_state_batch, done_batch = replay_buffer.sample(batch_size)
            q_values_next = tf.reduce_max(dqn(next_state_batch), axis=1)
            target_q_values = reward_batch + gamma * q_values_next * (1 - done_batch)
            with tf.GradientTape() as tape:
                q_values = tf.reduce_sum(dqn(state_batch) * tf.one_hot(action_batch, env.action_space.n), axis=1)
                loss = tf.reduce_mean(tf.square(target_q_values - q_values))
            grads = tape.gradient(loss, dqn.trainable_variables)
            optimizer.apply_gradients(zip(grads, dqn.trainable_variables))

# Decay epsilon
epsilon = max(epsilon * epsilon_decay, epsilon_min)

# Print the total reward of the episode
print(f'Episode {episode + 1} - Total Reward: {total_reward}')


state = env.reset()
done = False
total_reward = 0
while not done:
    env.render()
    action = tf.argmax(dqn(np.array([state]))[0]).numpy()
    next_state, reward, done, _ = env.step(action)
    total_reward += reward
    state = next_state
print(f'Test - Total Reward: {total_reward}')
env.close()