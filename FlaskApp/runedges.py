from multiprocessing import Process
from flask import Flask,request,render_template,jsonify
from database import execute_query
from utils import log_and_sum_time
def run_app(port):
    import requests
    from urllib.request import urlopen
    from flask_session import Session as g
    import random
    import time
    import requests
    import random
    import json
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

    @app.route("/response", methods=["POST"])
    def response():
        if request.method == "POST":
            fogId = request.json.get("fogId")
            fogUrl = request.json.get("fogUrl")
            st_time = time.time()
            res = handshakefog(fogUrl+"/handshake")
            end_time = time.time()
            log_and_sum_time("handshake", st_time, end_time)
            print("fog id:", fogId)
            print("fog url:", fogUrl)
            print(res)
            edgeId = request.json.get("edgeId")
            print(edgeId)
            st_time = time.time()
            res = sendWorkload(edgeId,fogId,fogUrl+"/recvload","23.mp4")
            end_time = time.time()
            print(res)
            log_and_sum_time("workload", st_time, end_time)
            return "received"

    def getLocation():
        url="http://ipinfo.io/json"
        res=urlopen(url)
        data=json.load(res)
        data=data['loc']
        data=data.split(",")
        return data

    def sendWorkload(edgeId,fogId,fogUrl,file_path):
        response_text = send_video(edgeId,fogId,fogUrl, file_path)
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

    def sendEdgeRequests():
        reqUrl="http://127.0.0.1:5000/add/edge"
        myUrl="http://127.0.0.1:2000"
        id=0
        latitude=float()
        longitude=float()
        cpuTime=float()
        s = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_maxsize=5)
        s.mount('http://', adapter)
        for i in range(0,1):
            id+=1
            latitude = random.uniform(70, 90)
            longitude = random.uniform(160, 180)
            cpuTime = random.uniform(0.00,30.00)
            payload={'id':id,'lat':latitude,'long':longitude,'cpuTime':cpuTime,'url':myUrl}
            s.post(reqUrl,json=payload)

    def send_video(edgeId,fogId,url, file_path):
        edgecpu = execute_query("SELECT cpu FROM ga.edge WHERE id = %s",[edgeId])
        edgecpu = edgecpu[0][0]
        with open(file_path, 'rb') as file:
            response = requests.post(url,files={"video": file},data={"edgeId":edgeId,"fogId":fogId,"edgecpu":edgecpu})
        return response.text

    def handshakefog(url):
        data = {"node_type": "edge"}
        # Send a POST request to the Fog node
        response = requests.post(url, json=data)
        return response
    

    app.run(port=port)
    

if __name__ == '__main__':
    processes = []
    n=5
    for port in range(2000, 2000+n):
        p = Process(target=run_app, args=(port,))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()
    