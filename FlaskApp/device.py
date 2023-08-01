class Device:
    def __init__(self,id,latitude,longitude,cpu,url):
        self.id=id
        self.latitude=latitude
        self.longitude=longitude
        self.cpu=cpu
        self.url=url
        self.preferenceList=[]
    def getPreferenceList(self,preferenceList):
        
        return self.preferenceList
    
    def getCoordinates(self):
        return [self.latitude, self.longitude]
    