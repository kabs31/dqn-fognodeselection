import time
import requests
from algorithms import dqn,fifo,da,ga
from config import requestList, distanceMap,listOfDevices, listOfFogNodes, handshake_times, workloadtimes,dqn_times,da_times,fifo_times
from database import execute_query
from device import Device
from fog import FogNode

def handle_request(device):
        
        execute_query("INSERT INTO ga.edge(latitude,longitude,cpu,url) VALUES (%s,%s,%s,%s)",(device.latitude,device.longitude,device.cpu,device.url))

        start_time = time.time()
        ga(device)
        end_time = time.time()
        fifo_times.append(end_time-start_time)

        start_time = time.time()
        da(device)
        end_time = time.time()
        da_times.append(end_time-start_time)
        
        start_time = time.time()
        dqn(device)
        end_time = time.time()
        dqn_times.append(end_time-start_time)

        sendResponse(device.url+"/response", device.id)



def searchFogId(id):
    for key, values in requestList.items():
        if id in values:
            return key


def get_url(id):
    for node in get_fog():
        if node.id == id:
            return node.url
    return None


def sendResponse(url, id):
    if not get_fog():
        data = {"result": "Cannot be allocated"}
        requests.post(url, json=data)
    else:
        result = searchFogId(int(id))
        fogurl = get_url(result)
        print(result, fogurl)
        data = {"edgeId":id,"fogId": result, "fogUrl": fogurl}
        s = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_maxsize=5)
        s.mount('http://', adapter)
        s.post(url, json=data)



def get_edge():
    results = execute_query("SELECT * FROM edge")
    edge_data = []
    for result in results:
        id, edgelat, edgelong, cpu, url = result
        edge_data.append(Device(id, edgelat, edgelong, cpu, url))
    return edge_data



def get_fog():
    results = execute_query("SELECT * FROM fog")
    fog_data = []
    for result in results:
        id, foglat, foglong, cpuFog, url,status,totalcpu= result
        fog_data.append(FogNode(id, foglat, foglong, cpuFog, url,status))
    return fog_data

def calculate_average(n, current_avg, new_num):
    # Calculate the average of n+1 numbers
    new_avg = ((current_avg * n) + new_num) / (n + 1)
    return new_avg

def log_and_sum_time(action_name, start_time, end_time):
        dur = (end_time - start_time)
        print(f"{action_name} time: {dur}")
        response = requests.post(f"http://127.0.0.1:5000/{action_name}", data={"time": dur})
        print(response)
        #sum += dur
        #print(f"sum: {sum}")

def get_st_fog():
    results = execute_query("SELECT * FROM fog")
    fog_data = []
    for result in results:
        id, foglat, foglong, cpuFog, url,status,totalcpu= result
        fog_data.append([id, foglat, foglong, totalcpu])
    return fog_data


