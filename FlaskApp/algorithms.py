import random
import time
import torch
import numpy as np
from da import ServicePlacement
from database import execute_query
from fog import FogNode
from config import distanceMap,listOfDevices, listOfFogNodes, handshake_times, workloadtimes,fifo_times,da_times,dqn_times,actionspace,requestList,requestList1,requestList2
from dqn.model import DQNNet
from ga import FogGeneticAlgorithm


def fifo(edge_node):
    unused_fog = get_unused_fog("fog1")
    fog_dict = {fog.id: fog for fog in unused_fog}
    for fog_node_id in fog_dict:
        fog_node = fog_dict[fog_node_id]
        if fog_node.cpuFog >= edge_node.cpu:
            if fog_node_id not in requestList1:
                requestList1[fog_node_id] = []
            requestList1[fog_node_id].append(edge_node.id)
            fog_node.cpuFog -= edge_node.cpu
            query = "UPDATE ga.fog SET cpu=%s WHERE id=%s"
            params = (fog_node.cpuFog, fog_node_id)
            execute_query(query, params)
            if fog_node.cpuFog == 0:
                execute_query("UPDATE ga.fog1 SET status='used' WHERE id = %s", [fog_node_id])
            #reupdate
            execute_query("UPDATE ga.fog1 SET cpu=cpu+%s WHERE id = %s", (edge_node.cpu,fog_node_id))
            execute_query("UPDATE ga.fog1 SET status='unused' WHERE id = %s AND status='used'", [fog_node_id])
            break

        

def algo1(listOfDevices,listOfFogNodes):
    requestList.clear()
    edge_index = 0
    for fog in listOfFogNodes:
        for i in range(len(listOfDevices)):
            edge = listOfDevices[edge_index % len(listOfDevices)]
            if edge.cpu <= fog.cpuFog:
                requestList[fog.id].append(edge.id)
                fog.cpuFog -= edge.cpu
                edge.cpu = 0
                edge_index += 1
                if edge_index == len(listOfDevices):
                    break
        if edge_index == len(listOfDevices):
            break
    return requestList

def ga(edge_node):
    action = 0
    fogs = {fog.id: fog for fog in get_unused_fog("fog1")}
    fog_nodes = []
    edge_nodes = 0
    for fog in fogs.values():
        fog_nodes.append({'id':fog.id, 'location': np.array([fog.latitude, fog.longitude]), 'capacity': fog.cpuFog})
    edge_nodes = {'id':edge_node.id,'location': np.array([edge_node.latitude, edge_node.longitude]), 'workload': edge_node.cpu}

    algo = FogGeneticAlgorithm(fog_nodes,edge_nodes,20,1000,0.1,0.8)
    action = algo.run()
    if float(edge_node.cpu) <= float(fogs[action].cpuFog) and edge_node.cpu != 0:
                requestList1.setdefault(action, []).append(int(edge_node.id))
                fogs[action].cpuFog -= float(edge_node.cpu)
                execute_query("UPDATE ga.fog1 SET cpu=%s, status=IF(cpu=0, 'used', status) WHERE id=%s", (fogs[action].cpuFog, action))
    execute_query("UPDATE ga.fog1 SET cpu=cpu+%s WHERE id = %s", (edge_node.cpu,action))
    execute_query("UPDATE ga.fog1 SET status='unused' WHERE id = %s AND status='used'", [action])
    


def da(edge_node):
    listOfDevices.append(edge_node)
    # Store devices and fogs in dictionaries for faster lookup
    devices = {device.id: device for device in listOfDevices}
    fogs = {fog.id: fog for fog in get_unused_fog("fog2")}

    # Compute distances between devices and fogs once and cache the results
    distances = {}
    for device in devices.values():
        distances[device.id] = {}
        for fog in fogs.values():
            distances[device.id][fog.id] = ServicePlacement.getDistance(device.getCoordinates(), fog.getCoordinates())

    # Compute priority lists for each device based on the cached distances
    for device in devices.values():
        priority_list = sorted(fogs.keys(), key=lambda fog_id: distances[device.id][fog_id])
        device.preferenceList = [int(fog_id) for fog_id in priority_list]
        distanceMap[int(device.id)] = device.preferenceList

    # Compute requests for each device based on the preference list and available resources
    for device in devices.values():
        for fog_id in device.preferenceList:
            fog = fogs[fog_id]
            if float(device.cpu) <= float(fog.cpuFog) and device.cpu != 0:
                requestList2.setdefault(fog_id, []).append(int(device.id))
                fog.cpuFog -= float(device.cpu)
                execute_query("UPDATE ga.fog2 SET cpu=%s, status=IF(cpu=0, 'used', status) WHERE id=%s", (fog.cpuFog, fog.id))
                #reupdate
                execute_query("UPDATE ga.fog2 SET cpu=cpu+%s WHERE id = %s", (device.cpu,fog_id))
                execute_query("UPDATE ga.fog2 SET status='unused' WHERE id = %s AND status='used'", [fog_id])
                break

    # Remove edge device from device list
    listOfDevices.remove(edge_node)
    


def dqn(edge_node):
    fogs = {fog.id: fog for fog in get_unused_fog("fog")}
    # Load saved model
    model = DQNNet(5,10)
    state_dict = torch.load(f='results/recent-model/dqn_model', map_location=torch.device('cpu')) #device is torch.device('cpu') or torch.device("cuda")
    model.load_state_dict(state_dict['model_state_dict'])
    edge_velocity = round(random.uniform(0, 150), 4)
    edge_direction = random.randint(0, 7)
    # Get input from user
    state = np.array([edge_node.cpu,edge_node.latitude,edge_node.longitude,edge_velocity,edge_direction])
    # Convert input to tensor
    state_tensor = torch.tensor(state)
    # Get best action
    with torch.no_grad():
        action = model(state_tensor).argmax().item()
    action+=1
    # Print best action
    print("Best action: ", action)
    if float(edge_node.cpu) <= float(fogs[action].cpuFog) and edge_node.cpu != 0:
                requestList.setdefault(action, []).append(int(edge_node.id))
                fogs[action].cpuFog -= float(edge_node.cpu)
                execute_query("UPDATE ga.fog SET cpu=%s, status=IF(cpu=0, 'used', status) WHERE id=%s", (fogs[action].cpuFog, action))



def get_unused_fog(name):
    query = "SELECT * FROM `{}` WHERE status = 'unused'".format(name)
    results = execute_query(query)
    fog_data = []
    for result in results:
        id, foglat, foglong, cpuFog, url,status,totalcpu= result
        fog_data.append(FogNode(id, foglat, foglong, cpuFog, url,status))
    return fog_data