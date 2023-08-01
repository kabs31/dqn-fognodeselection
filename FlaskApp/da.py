import math
from device import Device
from fog import FogNode
class ServicePlacement:
    listOfDevices=[]
    listOfFogNodes=[]
    requestList=dict()
    distanceMap=dict()
    dummy=[]
    def getDistance(coordinate1,coordinate2):
        x1=float(coordinate1[0])
        y1=float(coordinate1[1])
        x2=float(coordinate2[0])
        y2=float(coordinate2[1])
        x_dis=math.pow((x2-x1),2)
        y_dis=math.pow((y2-y1),2)
        return math.sqrt(x_dis+y_dis)
    def algorithm():
        f=open("D:\\device.csv","r")
        data=f.readlines()
        count=0
        for line in data:
            if(count!=0):
                word=line.replace('\n','').split(",")
    
                deviceLatitude=word[1]
                deviceLongitude=word[2]
                time=word[3]
                deviceID=word[4]
                device=Device(deviceID,deviceLatitude,deviceLongitude,time)
                ServicePlacement.listOfDevices.append(device)
            count+=1
        f.close()
        f1=open("D:\\fognode.csv","r")
        data2=f1.readlines()
        count2=0
        for line in data2:
            if(count2!=0):
                cloud=line.replace('\n','').split(",")
                
                nodeLatitude=cloud[1]
                nodeLongitude=cloud[2]
                time2=cloud[0]
                fogID=cloud[3]
            
                fognode=FogNode(fogID,nodeLatitude,nodeLongitude,time2)
                ServicePlacement.listOfFogNodes.append(fognode)
            count2+=1
        f1.close()
        for device in ServicePlacement.listOfDevices:
            listOfDistances=[]
            for fog in ServicePlacement.listOfFogNodes:
                
                distance=ServicePlacement.getDistance(device.getCoordinates(),fog.getCoordinates()) 
                listOfDistances.append(distance)
            priorityList=listOfDistances.copy()
            priorityList.sort()
            for i in range(len(priorityList)):
                for y in range(len(listOfDistances)):
                    if(priorityList[i]==listOfDistances[y]):
                        device.preferenceList.append(int(ServicePlacement.listOfFogNodes[y].id))
                
                ServicePlacement.distanceMap[int(device.id)]=device.preferenceList
                
        for k in range(len(ServicePlacement.listOfDevices)):
            currdevice=ServicePlacement.listOfDevices[k]
            
            for fg in range(len(ServicePlacement.listOfDevices[k].preferenceList)):
                for m in range(len(ServicePlacement.listOfFogNodes)):
                    if(int(ServicePlacement.listOfDevices[k].preferenceList[fg])==int(ServicePlacement.listOfFogNodes[m].id)):
                        fog=ServicePlacement.listOfFogNodes[m]
                        break
               
                if currdevice.preferenceList[fg] not in ServicePlacement.requestList.keys():
                    ServicePlacement.requestList[currdevice.preferenceList[fg]]=[]
            
                if(float(currdevice.cpu)<float(fog.cpuFog)):
                    ServicePlacement.requestList[currdevice.preferenceList[fg]].append(int(currdevice.id))
                    fog.cpuFog=float(fog.cpuFog)-float(currdevice.cpu)
                    x=fog.cpuFog
                    ServicePlacement.dummy.append(x) 
                    break   
        return str(ServicePlacement.requestList)
if __name__ == "__main__":
    ServicePlacement.algorithm()