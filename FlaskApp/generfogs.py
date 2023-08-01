import requests
from database import execute_query
import random
from config import actionspace
n=10
for i in range(n):
            latitude = round(random.uniform(8, 15), 4)
            longitude = round(random.uniform(70, 90), 4)
            cpuTime = random.uniform(300, 500)
            myUrl = f"http://127.0.0.1:{i+3000}"
            
            payload={'id':i+1,'lat':latitude,'long':longitude,'cpuTime':cpuTime,'url':myUrl}
            res = requests.post("http://127.0.0.1:5000/add/fog",json=payload)