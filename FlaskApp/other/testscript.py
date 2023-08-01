import requests

fogDatas = []
deviceDatas = []

fogDatas.append({
"id": "1",
"lat": "9.09",
"long": "70.09",
"cpuTime": "50"
})

fogDatas.append({
"id": "2",
"lat": "9.99",
"long": "78.87",
"cpuTime": "52"
})

fogDatas.append({
"id": "3",
"lat": "9.87",
"long": "76.67",
"cpuTime": "40"
})

fogDatas.append({
"id": "4",
"lat": "9.99",
"long": "78.87",
"cpuTime": "50"
})


deviceDatas.append({
"id": "4",
"lat": "9.88",
"long": "45.56",
"cpuTime": "30"
})

deviceDatas.append({
"id": "2",
"lat": "9.27",
"long": "90.9",
"cpuTime": "70"
})

deviceDatas.append({
"id": "3",
"lat": "9.88",
"long": "87.79",
"cpuTime": "35"
})

deviceDatas.append({
"id": "1",
"lat": "9.76",
"long": "80.98",
"cpuTime": "22"
})

[requests.post("http://127.0.0.1:5000/fog/add/", json=data) for data in fogDatas]
[requests.post("http://127.0.0.1:5000/device/add/", json=data) for data in deviceDatas]