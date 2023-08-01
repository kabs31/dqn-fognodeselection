class FogNode:
    def __init__(self,id,latitude,longitude,cpuFog,url,status):
        self.id=id
        self.latitude=latitude
        self.longitude=longitude
        self.cpuFog=cpuFog
        self.url = url
        self.status = status
        self.totalcpu=cpuFog
    def getCoordinates(self):
        return [self.latitude, self.longitude]