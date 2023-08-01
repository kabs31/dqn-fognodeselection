import gym
import numpy as np
import random
import math

class FogNodeSelectionEnv(gym.Env):
    def __init__(self):
         # Define the observation space
        self.observation_space = gym.spaces.Box(low=np.array([0, -90, -180, 0, 0]), high=np.array([1000, 90, 180, 100, 7]), dtype=np.float32)
        # Define the action space
        # Define the action space as a discrete space with size 2 for selecting one of the fog nodes
        self.fog_nodes = []
        self.action_space = gym.spaces.Discrete(10)

        # Initialize the state variables
        self.workload = 0
        self.edge_location = np.array([random.uniform(-90, 90), random.uniform(-180, 180)])
        self.edge_velocity = random.uniform(0, 150)
        self.edge_direction = random.randint(0, 8)
        self.selected_fog_node = {}
        self.steps_left = 1000
    
    def step(self, action):
        # Check if the action is valid
        if not self.action_space.contains(action):
            raise ValueError('Invalid action')
        
        # Select the fog node based on the action
        self.selected_fog_node = self.fog_nodes[action]
        
        # Calculate the processing time at the fog node based on workload and capacity
        processing_time = self.workload / self.selected_fog_node['capacity'] * 100
        
        # Calculate the latency as the sum of distance and processing time
        distance = np.linalg.norm(self.selected_fog_node['location'] - self.edge_location)
        latency = distance + processing_time
        
        # Calculate the reward based on the latency
        reward = 1 / latency
        reward = format(reward, '.6f')
        reward=float(reward)
        # Subtract the workload processed by the selected fog node
        self.workload -= self.selected_fog_node['capacity']
        
        # Update the time step counter
        self.steps_left -= 1
        
        # Update the velocity, direction, and location of the edge node
        directions = [0, 45, 90, 135, 180, 225, 270, 315]
        direction_radians = directions[self.edge_direction]
        self.edge_velocity = self.edge_velocity+round(random.uniform(-5, 5), 4)
        self.edge_location = self._calculate_new_location(self.selected_fog_node['location'][0], self.selected_fog_node['location'][1], direction_radians, self.edge_velocity, 3)

        
        # Check if the episode is over
        truncated = self.steps_left == 0 
        terminated = self.workload <= 0
        
        return self._get_state(), reward, terminated,truncated, {}

    
    def reset(self):
        # Reset the state variables
        self.workload = random.uniform(0, 1000)
        self.edge_location = np.array([round(random.uniform(8, 15), 4), round(random.uniform(70, 90), 4)])
        self.edge_velocity = random.uniform(0, 100)
        self.edge_direction = random.randint(0,7)
        self.selected_fog_node = None
        self.steps_left = 1000
        return self._get_state()
    
    def _get_state(self):
        # Return the current state as a numpy array
        return np.array([self.workload, self.edge_location[0],self.edge_location[1],self.edge_velocity,self.edge_direction])
    
    def seed(self, seed=None):
        self.np_random, seed = gym.utils.seeding.np_random(seed)
        random.seed(seed)
        return [seed]
    
    def _calculate_new_location(self,lat1,lon1,direction, velocity, time_taken):
        R = 6371  # Earth's radius in km
        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)
        bearing = direction  # bearing in radians
        distance = velocity*(time_taken*0.000277778)  # distance in km

        lat2 = math.asin(math.sin(lat1) * math.cos(distance/R) + math.cos(lat1) * math.sin(distance/R) * math.cos(bearing))
        lon2 = lon1 + math.atan2(math.sin(bearing) * math.sin(distance/R) * math.cos(lat1), math.cos(distance/R) - math.sin(lat1) * math.sin(lat2))

        new_latitude = math.degrees(lat2)
        new_longitude = math.degrees(lon2)
        return new_latitude, new_longitude
    import numpy as np

    def add_fog_node(self,capacity, latitude, longitude):
        """
        Add a new fog node to the given data structure, with the given capacity and location.

        Args:
            nodes (list of dict): The list of nodes to add a fog node to.
            capacity (int): The capacity of the new node.
            latitude (float): The latitude of the new node.
            longitude (float): The longitude of the new node.

        Returns:
            The updated list of nodes, with the new fog node appended to the end.
        """
        # Create a new dictionary for the fog node and append it to the list of nodes
        fog_node = {'capacity': capacity, 'location': np.array([latitude, longitude])}
        self.fog_nodes.append(fog_node)


    
    def _sigmoid(self,x):
        return 1 / (1 + math.exp(-x))




env = FogNodeSelectionEnv()
"""
obs = env.reset()
done = False
total_reward = 0
print("initial--observation",obs)
while not done:
    action = env.action_space.sample()
    obs, reward, done, info = env.step(action)
    total_reward += reward
    print(action,obs, reward)
    #env.render()
print(f'Total reward: {total_reward}')

"""
