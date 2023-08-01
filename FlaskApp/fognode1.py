import random,time
import requests
from flask import Flask,request,render_template,jsonify
from urllib.request import urlopen
from flask_session import Session as g
from database import execute_query,connect_db
from VehicleDetection import vd

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
g(app)


g.latitude = None
g.longitude = None
g.new_latitude = 37.4219999
g.new_longitude = -122.0840575
g.myUrl=""
g.id=""
g.lat=0
g.long=0
g.cpuTime=0
g.reqUrl=""

@app.route("/",methods=['POST','GET'])
def home():
    if(request.method=='POST'):
        g.id=request.form.get("id")
        g.latitude=request.form.get("lat")
        g.longitude=request.form.get("long")
        g.reqUrl=request.form.get("requrl")
        g.reqUrl+="/add/fog"
        g.myUrl=request.form.get("myurl")
        g.myUrl=str(g.myUrl)
        print(g.myUrl)
        g.cpuTime=request.form.get("cpuTime")
        payload={'id':g.id,'lat':g.latitude,'long':g.longitude,'cpuTime':g.cpuTime,'url':g.myUrl}
        res = requests.post(g.reqUrl,json=payload)
        return jsonify(res.status_code)
    else:
        return render_template("foghome.html")

@app.route("/recvload",methods=['POST'])
def recvload():
    if(request.method=='POST'):
        video_file = request.files["video"]
        filename = video_file.filename
        edgeId = request.form['edgeId']
        fogId = request.form["fogId"]
        edgecpu = request.form["edgecpu"]
        print(f"edgecpu--{edgecpu}")
        filename+=edgeId
        video_file.save(f'videos/{filename}')
        result = vd(f'videos/{filename}')
        print(f"edgeid {edgeId} workload result--{result}")
        execute_query("UPDATE ga.fog SET cpu=cpu+%s WHERE id = %s", (edgecpu,fogId))
        execute_query("UPDATE ga.fog SET status='unused' WHERE id = %s AND status='used'", [fogId])
        return f'Car count result--{result}'
    else:
        return "Invalid"

def sendFogRequests():
    reqUrl="http://127.0.0.1:5000/add/fog"
    myUrl="http://127.0.0.1:3000"
    id=0
    latitude=float()
    longitude=float()
    cpuTime=float()
    s = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_maxsize=5)
    s.mount('http://', adapter)
    for i in range(0,3):
        id+=1
        latitude = random.uniform(70, 90)
        longitude = random.uniform(160, 180)
        cpuTime = random.uniform(0.00,50.00)
        payload={'id':id,'lat':latitude,'long':longitude,'cpuTime':cpuTime,'url':myUrl}
        s.post(reqUrl,json=payload)

@app.route("/handshake", methods=["POST"])
def handshake():
    # Get the data sent from the Edge node
    data = request.get_json()
    
    # Check if the data contains the "node_type" field and its value is "edge"
    if "node_type" in data and data["node_type"] == "edge":
        # Send a response to the Edge node
        return "Handshake successful!"
    
    # If the "node_type" field is missing or its value is not "edge", send an error message
    return "Invalid request."


if __name__=='__main__':
    #sendFogRequests()
    app.run(debug=True,port="3000")