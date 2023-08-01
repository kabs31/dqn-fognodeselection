from flask import Flask,request, render_template,redirect,url_for
import mysql.connector
import json,time
from da import ServicePlacement
from device import Device
from fog import FogNode
app = Flask(__name__)

listOfDevices=[]
listOfFogNodes=[]
requestList=dict()
distanceMap=dict()
mydb=mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="traffic"
    )
@app.route('/')

def home():
    return render_template('home.html')
def algo():
    for device in listOfDevices:
            listOfDistances=[]
            for fog in listOfFogNodes:
                
                distance=ServicePlacement.getDistance(device.getCoordinates(),fog.getCoordinates()) 
                listOfDistances.append(distance)
            priorityList=listOfDistances.copy()
            priorityList.sort()
            for i in range(len(priorityList)):
                for y in range(len(listOfDistances)):
                    if(priorityList[i]==listOfDistances[y]):
                        device.preferenceList.append(int(listOfFogNodes[y].id))
                
                distanceMap[int(device.id)]=device.preferenceList
                
                
    
    for k in range(len(listOfDevices)):
        currdevice=listOfDevices[k]
        for fg in range(len(listOfDevices[k].preferenceList)):
            for m in range(len(listOfFogNodes)):
                if(int(listOfDevices[k].preferenceList[fg])==int(listOfFogNodes[m].id)):
                    fog=listOfFogNodes[m]
                    break
            if currdevice.preferenceList[fg] not in requestList.keys():
                    requestList[currdevice.preferenceList[fg]]=[]
            
            if(float(currdevice.cpu)<float(fog.cpuFog) and currdevice.cpu!=0):
                    requestList[currdevice.preferenceList[fg]].append(int(currdevice.id))
                    fog.cpuFog=float(fog.cpuFog)-float(currdevice.cpu)      
                    currdevice.cpu=0
                    break   
    
    
@app.route('/device/add/',methods=['GET','POST'])
def addDevice():
    mycursor=mydb.cursor() 
    if request.method == 'POST':
        deviceid=request.form.get('id')
        devicelatitude=request.form.get('lat')
        devicelongitude=request.form.get('long')
        devicecpu=request.form.get('cpuTime')
        devicebasecpu=devicecpu
        device=Device(deviceid,devicelatitude,devicelongitude,devicecpu,devicebasecpu)
        listOfDevices.append(device)  
        mycursor.execute("insert into devicelist (deviceid,devicelat,devicelong,devicecpu)VALUES(%s,%s,%s,%s)",(deviceid,devicelatitude,devicelongitude,devicecpu))
        mydb.commit()
        mycursor.close()
    elif request.method=='GET':
         return render_template('devicedata.html')  
    
    return{ "message":"Device Added Successfully","status":500}


@app.route('/fog/add/',methods=['POST','GET'])
def addFogNode():
    mycursor=mydb.cursor() 
    if request.method == 'POST':
        fogid=request.form.get('fogid')
        foglatitude=request.form.get('foglat')
        foglongitude=request.form.get('foglong')
        fogcpu=request.form.get('fogcpuTime')
        fog=FogNode(fogid,foglatitude,foglongitude,fogcpu)
        listOfFogNodes.append(fog) 
        mycursor.execute("insert into foglist (fogid,foglat,foglong,fogcpu)VALUES(%s,%s,%s,%s)",(fogid,foglatitude,foglongitude,fogcpu))
        mydb.commit()
        mycursor.close()
 
    elif request.method=='GET':
        return render_template('fogdata.html')  
    
    return {"message":"Fog Node Added Successfully","status":500}

@app.route('/getPreferenceList/',methods=['GET'])
def getPreferenceList():
    [device.preferenceList.clear() for device in listOfDevices]
    algo()
    return distanceMap
@app.route('/getRequestList/',methods=['GET'])
def getRequestList():

    algo()
   
    return requestList
@app.route('/getFogNode/', methods=["GET"])
def getFogNode():
    data=[]
    deviceId = int(request.args.get('id'))
    device = None
    for d in listOfDevices:
        if(int(d.id) == deviceId):
            device =  d
            break
        
    if(device == None):
        return {"message":"Device Not Found","status":500}

    fogId = None

    for fg in requestList.keys():
        if (deviceId in requestList[fg]):
            fogId = fg
    if fogId == None:
        return {"message":"Fog is not allocated","status":500}
    else:
        for fog in listOfFogNodes:
            if(int(fog.id) == fogId):
                data.append({"id": fog.id,
                "lat": fog.latitude,
                "long": fog.longitude})
        return {"fog node":data,"status":500}
        
@app.route('/getDevices/', methods=["GET"])
def getDevices():
    result=[]
    fogId = int(request.args.get('id'))

    if fogId in requestList.keys():
        for deviceId in requestList[fogId]:
            for d in listOfDevices:
                if(int(d.id) == int(deviceId)):

                    result.append({
                        "id": d.id,
                        "lat": d.latitude,
                        "long": d.longitude,
                        "cpuTime": d.cpu2
                        
                    })
            
            
        return {"devices":result,"status":500}

    else:
        return "No Device is allocated to fog"         
if __name__=="__main__":
    app.run(debug=True,host='0.0.0.0')