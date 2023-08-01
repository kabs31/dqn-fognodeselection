import random
import torch
from dqn.model import DQNNet
import numpy as np

model = DQNNet(5,10)
state_dict = torch.load(f='results/recent-model/dqn_model', map_location=torch.device('cpu')) #device is torch.device('cpu') or torch.device("cuda")
model.load_state_dict(state_dict['model_state_dict'])
    # Get input from user
for i in range(100):
        latitude = round(random.uniform(8, 15), 4)
        longitude = round(random.uniform(70, 90), 4)
        cpuTime = round(random.uniform(0, 500), 4)
        edge_velocity = round(random.uniform(0, 150), 4)
        edge_direction = random.randint(0, 7)
        state = np.array([cpuTime,latitude,longitude,edge_velocity,edge_direction])
            # Convert input to tensor
        state_tensor = torch.tensor(state)
            # Get best action
        with torch.no_grad():
                action = model(state_tensor).argmax().item()
        action+=1
            # Print best action    
        print("Best action: ", action)