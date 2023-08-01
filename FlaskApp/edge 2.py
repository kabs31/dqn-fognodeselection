import json
import time
import requests
from flask import Flask,request,render_template,jsonify
from urllib.request import urlopen
from flask_session import Session as g

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
        g.reqUrl+="/add/edge"
        g.myUrl=request.form.get("myurl")
        g.myUrl=str(g.myUrl)
        print(g.myUrl)
        g.cpuTime=request.form.get("cpuTime")
        payload={'id':g.id,'lat':g.latitude,'long':g.longitude,'cpuTime':g.cpuTime,'url':g.myUrl}
        res = requests.post(g.reqUrl,json=payload)
        return jsonify(res.status_code)
    else:
        return render_template("edgehome.html")

@app.route("/response",methods=['POST'])
def response():
    if(request.method=='POST'):
        st_time = time.time()
        fogId = request.json.get("fogId")
        fogUrl = request.json.get("fogUrl")
        res = handshakefog(fogUrl+"/handshake")
        end_time = time.time()
        print("fog id:",fogId)
        print("fog url:",fogUrl)
        print(res)
        print("handshake time:",(end_time-st_time)*1000)
        #sendWorkload(fogUrl+"/recvload")
        return "received"

def getLocation():
    url="http://ipinfo.io/json"
    res=urlopen(url)
    data=json.load(res)
    data=data['loc']
    data=data.split(",")
    return data

def sendWorkload(fogUrl,file_path):
    response_text = send_video(fogUrl, file_path)
    return response_text

@app.route('/change', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        g.new_latitude = request.form['latitude']
        g.new_longitude = request.form['longitude']
        update_coordinates()
    return render_template('edgechange.html')

def update_coordinates():
    # Update the variables with new coordinates
    if g.new_latitude != g.latitude or g.new_longitude != g.longitude:
        g.latitude = g.new_latitude
        g.longitude = g.new_longitude
        data = {'latitude': g.latitude, 'longitude': g.longitude,'edgeid':g.id}
        requests.post('http://127.0.0.1:5000/getEdgeChangeLoc', json=data)
        return 'Latitude and Longitude updated.'
    else:
        return 'no location change.'
def handshakefog(url):
    data = {"node_type": "edge"}
    # Send a POST request to the Fog node
    response = requests.post(url, json=data)
    return response
    
def send_video(url, file_path):
    with open(file_path, 'rb') as file:
        response = requests.post(url, files={'video': file})
    return response.text
if __name__ == '__main__':
    app.run(debug=True,port=2001)