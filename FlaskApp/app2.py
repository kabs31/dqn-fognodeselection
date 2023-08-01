from flask import Flask,render_template, request,redirect,url_for
app = Flask(__name__)

@app.route('/',methods=["POST", "GET"])
def home():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        video=request.files['video']
        vname=video.filename
        vblob=video.read()
        writeTostatic(vblob,vname)
        return redirect(url_for("home"))


def writeTostatic(data,filename):
    vpath="static/videos/"+str(filename)
    with open(vpath,'wb') as file:
        file.write(data)


if __name__ == "__main__":
    app.run(debug=True)