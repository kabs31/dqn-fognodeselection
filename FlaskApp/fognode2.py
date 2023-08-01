import json
from flask import Flask,request,render_template,jsonify
from urllib.request import urlopen

from VehicleDetection import vd
from database import execute_query
app = Flask(__name__)
import requests
myUrl=""
id=""
lat=0
long=0
cpuTime=0

@app.route("/",methods=['POST','GET'])
def home():
    if(request.method=='POST'):
        global id
        id=request.form.get("id")
        global lat
        lat=request.form.get("lat")
        global long
        long=request.form.get("long")
        reqUrl=request.form.get("requrl")
        reqUrl+="/add/fog"
        global myUrl
        myUrl=request.form.get("myurl")
        myUrl=str(myUrl)
        print(myUrl)
        global cpuTime
        cpuTime=request.form.get("cpuTime")
        payload={'id':id,'lat':lat,'long':long,'cpuTime':cpuTime,'url':myUrl}
        res = requests.post(reqUrl,json=payload)
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
        filename+=edgeId
        video_file.save(f'videos/{filename}')
        result = vd(f'videos/{filename}')
        print(f"edgeid {edgeId} workload result--{result}")
        execute_query("UPDATE ga.fog SET cpu=cpu+%s WHERE id = %s", (edgecpu,fogId))
        execute_query("UPDATE ga.fog SET status='unused' WHERE id = %s AND status='used'", [fogId])
        return f'Car count result--{result}'
    else:
        return "Invalid"

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
    app.run(debug="True",port="3001")