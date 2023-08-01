import base64
import io
import pickle
import time
from flask import Flask, jsonify,request, render_template,redirect,url_for
from flask_session import Session as g
import matplotlib.pyplot as plt
import numpy as np
from database import execute_query,connect_db
from device import Device
from fog import FogNode
from config import requestList, distanceMap,listOfDevices, listOfFogNodes, requesttimes,handshake_times, workloadtimes,fogcounter,dqn_times,da_times,fifo_times,actionspace,edge_list,fog_list
from utils import get_fog, get_st_fog, get_url, handle_request, sendResponse
from dqn.fogenv import env,FogNodeSelectionEnv
from dqn.dqn import traindqn
import plotly.graph_objs as go

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
g(app)
g.fogcounter=0

# Define device and request status
device_status = "Connected"
request_status = "Processing"

@app.route('/dashboard')
def dashboard():
    # Generate some sample data
    x = np.arange(1, 100, 1)
    
    # Create the Plotly line chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=da_times, mode='lines+markers', name='da_times'))
    fig.add_trace(go.Scatter(x=x, y=fifo_times, mode='lines+markers', name='ga_times'))
    fig.add_trace(go.Scatter(x=x, y=dqn_times, mode='lines+markers', name='dqn_times'))
    
    # Update the chart layout
    fig.update_layout(
        xaxis_title='Edge ID',
        yaxis_title='Seconds',
        plot_bgcolor='rgb(24,27,35)',
        paper_bgcolor='rgb(24,27,35)',
        font_color='white',
        margin=dict(l=40, r=40, t=60, b=20),
        legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5),
        colorway=['#ff7f0e', '#2ca02c', '#d62728'],
        xaxis=dict(gridcolor='white'),
        yaxis=dict(gridcolor='white')
    )
    # Render the HTML template with the Plotly chart embedded
    return render_template('dashboard.html', plot=fig.to_html())

@app.route("/reqprocestime")
def reqprocestime():
    # Create plot of request processing times using Plotly
    fig = go.Figure(data=[go.Scatter(x=list(range(1, len(requesttimes)+1)), y=requesttimes)])
    fig.update_layout(title='Request Processing Times', xaxis_title='Request Number', yaxis_title='Processing Time (seconds)', 
                          template='plotly_dark')
        
    # Convert plot to HTML
    plot_div = fig.to_html(full_html=False, default_height=500, default_width=700)
        
    # Render the HTML template with the plot
    return render_template('dashboard.html', plot=plot_div)


@app.route("/handshaketime")
def handshaketime():
    # Create plot of handshake times using Plotly
    fig = go.Figure(data=[go.Scatter(x=list(range(1, len(handshake_times)+1)), y=handshake_times)])
    fig.update_layout(title='Handshake Times', xaxis_title='Request Number', yaxis_title='Time (seconds)', 
                          template='plotly_dark')
        
    # Convert plot to HTML
    plot_div = fig.to_html(full_html=False, default_height=500, default_width=700)
        
    # Render the HTML template with the plot
    return render_template('dashboard.html', plot=plot_div)


@app.route("/workloadtime")
def workloadtime():
    # Create plot of workload times using Plotly
    fig = go.Figure(data=[go.Scatter(x=list(range(1, len(workloadtimes)+1)), y=workloadtimes)])
    fig.update_layout(title='Workload Times', xaxis_title='Request Number', yaxis_title='Time (seconds)', 
                          template='plotly_dark')
        
    # Convert plot to HTML
    plot_div = fig.to_html(full_html=False, default_height=500, default_width=700)
        
    # Render the HTML template with the plot
    return render_template('dashboard.html', plot=plot_div)

@app.route('/resourceusage')
def resource_usage():
    device_cpu = [device.cpu for device in edge_list]
    fog_cpu = [fog[3] for fog in get_st_fog()]
    device_names = [f"Device {device.id}" for device in edge_list]
    fog_names = [f"Fog {fog[0]}" for fog in get_st_fog()]

    fig, ax = plt.subplots()
    ax.bar(device_names, device_cpu, color='b', label='Device')
    ax.bar(fog_names, fog_cpu, color='r', label='Fog Node')
    ax.set_ylabel('CPU Usage')
    ax.set_title('Device and FogNode Resource Usage')
    ax.legend()

    # Save the figure to a file
    fig.savefig('resource_usage.png')

    # Convert the figure to a base64-encoded string
    with open('resource_usage.png', 'rb') as f:
        figdata = base64.b64encode(f.read()).decode()

    return render_template('Usage.html', figdata=figdata)

@app.route("/fogutilization")
def fogutilization():
    # Get the list of fog nodes
    fog_nodes = get_st_fog()

    # Count the number of edges assigned to each fog node
    utilization = [len(requestList[fog[0]]) if fog[0] in requestList else 0 for fog in fog_nodes]

    # Create a heatmap of the utilization of each fog node
    fig, ax = plt.subplots()
    heatmap = ax.imshow([utilization], cmap='YlOrRd')
    ax.set_xticks(range(len(fog_nodes)))
    ax.set_xticklabels([f"Fog {fog[0]}" for fog in fog_nodes])
    ax.set_yticks([0])
    ax.set_yticklabels(["Utilization"])
    cbar = ax.figure.colorbar(heatmap, ax=ax)
    cbar.ax.set_ylabel("Number of Edges Assigned", rotation=-90, va="bottom")

    # Save the plot as a PNG image in memory
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    # Encode the PNG image in base64 and create a data URI for it
    img_base64 = base64.b64encode(img.read()).decode()

    # Render the HTML template with the data URI for the image
    return render_template("Usage.html", figdata=img_base64)


@app.route('/train/progress')
def plot_progress():
    with open('{}/progress.pkl'.format("C:/Users/91638/Desktop/DA/flask/FlaskApp/results/recent-model"), 'rb') as f:
        progress = pickle.load(f)

    eps = [x[0] for x in progress]
    scores = [x[1] for x in progress]
    epsilons = [x[2] for x in progress]
    
    fig, ax = plt.subplots()
    ax.plot(eps, scores, label='Avg Score')
    ax.plot(eps, epsilons, label='Epsilon')
    ax.set_xlabel('Episode')
    ax.set_ylabel('Value')
    ax.legend()
    
    # Save the plot as a PNG image in memory
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    # Encode the PNG image in base64 and create a data URI for it
    img_base64 = base64.b64encode(img.read()).decode()
    
    return render_template("dqnreport.html", figdata=img_base64)

@app.route('/train/episode_length')
def plot_episode_length():
    with open('{}/ep_length.pkl'.format("C:/Users/91638/Desktop/DA/flask/FlaskApp/results/recent-model"), 'rb') as f:
        episode_lengths = pickle.load(f)
    print(episode_lengths)
    episode_length = [x for x in episode_lengths]  # assuming episode length is stored at index 3 of each tuple
    
    fig, ax = plt.subplots()
    ax.plot(episode_length)
    ax.set_xlabel('Episode')
    ax.set_ylabel('Episode Length')
    
    # Save the plot as a PNG image in memory
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    # Encode the PNG image in base64 and create a data URI for it
    img_base64 = base64.b64encode(img.read()).decode()
    
    return render_template("dqnreport.html", figdata=img_base64)

@app.route('/action_frequency_table')
def action_frequency_table():
    with open('{}/action_frequency.pkl'.format("C:/Users/91638/Desktop/DA/flask/FlaskApp/results/recent-model"), 'rb') as f:
        action_frequency = pickle.load(f)
    num_actions = len(action_frequency)

    # Create bar chart of action frequency
    fig, ax = plt.subplots()
    ax.bar(range(num_actions), action_frequency)
    ax.set_xticks(range(num_actions))
    ax.set_xlabel('Action')
    ax.set_ylabel('Frequency')
    ax.set_title('Action Frequency Table')

    # Convert chart to base64 string for embedding in HTML
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    chart_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return render_template('dqnreport.html', figdata=chart_data)


@app.route('/loss_graph')
def plot_loss():
    with open('{}/loss_history.pkl'.format("C:/Users/91638/Desktop/DA/flask/FlaskApp/results/recent-model"), 'rb') as f:
        loss_history = pickle.load(f)

    fig, ax = plt.subplots()
    ax.plot(loss_history)
    ax.set_xlabel('Training Step')
    ax.set_ylabel('Loss')

    # Save the plot as a PNG image in memory
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    # Encode the PNG image in base64 and create a data URI for it
    img_base64 = base64.b64encode(img.read()).decode()

    return render_template("dqnreport.html", figdata=img_base64)


# Define route for dashboard
@app.route('/edgetab')
def edgetab():
    return render_template('edgedash.html', request_list=edge_list,device_status=device_status,request_status=request_status,fog=None)

@app.route('/fogtab')
def fogtab():
    fog_data = get_st_fog()
    return render_template('table.html', request_list=fog_data,fog_device_status=device_status,request_status=request_status,edge=None)


@app.route('/find_edges', methods=['POST'])
def find_edges():
    edge = []
    fog_id = request.form['fog_id']
    print(fog_id)
    for key, values in requestList.items():
        if int(fog_id)==key:
            for i in values:
                edge.append(execute_query(f"select * from ga.edge where id={i}"))
            break
    return render_template('table.html', request_list=get_st_fog(),fog_device_status=device_status,request_status=request_status,edge=edge)

#run_with_ngrok(app)
@app.route('/')
@app.route('/home')
def home():
    mydb = connect_db()
    if mydb.is_connected():
        print("Connected to the database")
    else:
        print("connection failed")
    
    mydb.close()
    return render_template('home.html')


@app.route('/add/edge', methods=['GET', 'POST'])
def addEdge():
    if request.method == 'POST':
        start_time = time.time()
        deviceid = int(request.json.get('id'))
        devicelatitude = float(request.json.get('lat'))
        devicelongitude = float(request.json.get('long'))
        devicecpu = float(request.json.get('cpuTime'))
        deviceurl = request.json.get('url')
        device = Device(deviceid, devicelatitude, devicelongitude,
                        devicecpu,deviceurl)
        print("Edge", device.id, "added to the request queue")
        print(f"Processing request for device {device}")  
        
        handle_request(device)
        end_time = time.time()
        edge_list.append(device)
        requesttimes.append(end_time-start_time)
        print(requestList)
        
        
        
    elif request.method == 'GET':
        return render_template('devicedata.html')

    return {"message": "Device Added Successfully", "status": 500}




@app.route('/getEdgeChangeLoc', methods=['POST'])
def EdgeChangeLoc():
    latitude = float(request.json['latitude'])
    longitude = float(request.json['longitude'])
    edgeid = float(request.json['edgeid'])
    edgeurl=""
    for device in listOfDevices:
        if device.id == edgeid:
            edgeurl = device.url
            device.latitude = latitude
            device.longitude = longitude
            break
    #algo()
    #algo1()
    print(requestList)
    sendResponse(edgeurl+"/response", edgeid)
    print(f'Received: {latitude}, {longitude}, {edgeid}')
    
    return 'Coordinates updated'



@app.route('/add/fog', methods=['POST', 'GET'])
def addFog():
    if request.method == 'POST':
        g.fogcounter+=1
        fogid = int(request.json.get('id'))
        foglatitude = float(request.json.get('lat'))
        foglongitude = float(request.json.get('long'))
        fogcpu = float(request.json.get('cpuTime'))
        fogurl = request.json.get('url')
        fog = FogNode(fogid, foglatitude, foglongitude, fogcpu, fogurl,"unused")
        fog_list.append(fog)
        print(fog.id, fog.latitude, fog.longitude, fog.cpuFog, fogurl)
        execute_query("insert into ga.fog(latitude,longitude,cpu,url,status,totalcpu) VALUES(%s,%s,%s,%s,%s,%s)",(foglatitude,foglongitude,fogcpu,fogurl,"unused",fogcpu))
        execute_query("insert into ga.fog1(latitude,longitude,cpu,url,status,totalcpu) VALUES(%s,%s,%s,%s,%s,%s)",(foglatitude,foglongitude,fogcpu,fogurl,"unused",fogcpu))
        execute_query("insert into ga.fog2(latitude,longitude,cpu,url,status,totalcpu) VALUES(%s,%s,%s,%s,%s,%s)",(foglatitude,foglongitude,fogcpu,fogurl,"unused",fogcpu))
        env.add_fog_node(fogcpu,foglatitude,foglongitude)
        print('action space--',len(env.fog_nodes))
        if(g.fogcounter==10):
            traindqn()
            g.fogcounter=0
    elif request.method == 'GET':
        return render_template('fogdata.html')

    return {"message": "Fog Node Added Successfully", "status": 500}


@app.route('/handshake', methods=['POST'])
def handshake():
    time = float(request.form['time'])
    handshake_times.append(time)
    return 'Handshake time received'

@app.route('/avghndtime')
def average_handshake_time():
    if not handshake_times:
        return 'No handshake times received yet'

    sum_time = sum(handshake_times)
    handshake_times.clear()
    return f'cumulative handshake time: {round(sum_time, 4)} seconds'

@app.route('/workload', methods=['POST'])
def workload():
    workload_time = float(request.form['time'])
    workloadtimes.append(workload_time)
    return "Workload time received"

@app.route('/sumloadtime')
def sum_workload_time():
    if not workloadtimes:
        return 'No workload times received yet'
        
    sum_time = sum(workloadtimes)
    workloadtimes.clear()
    return f'cumulative workload time: {round(sum_time, 4)} seconds'

@app.route('/sumstartuptime')
def sum_startup_time():
    if not dqn_times:
        return 'No workload times received yet'
        
    sum_time = sum(dqn_times)
    dqn_times.clear()
    return f'cumulative workload time: {round(sum_time, 4)} seconds'


if __name__ == "__main__":
    app.run(debug=True,port=5000)
