import json
import os
import requests
from flask import Flask, render_template, redirect, request, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "app/static/Uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ADDR = "http://127.0.0.1:8800"
request_tx = []
files = {}

def get_tx_req():
    global request_tx
    chain_addr = "{0}/chain".format(ADDR)
    resp = requests.get(chain_addr)
    if resp.status_code == 200:
        content = []
        chain = json.loads(resp.content.decode())
        for block in chain["chain"]:
            for trans in block["transactions"]:
                trans["index"] = block["index"]
                trans["hash"] = block["prev_hash"]
                content.append(trans)
        request_tx = sorted(content, key=lambda k: k["hash"], reverse=True)

@app.route("/")
def index():
    get_tx_req()
    return render_template("index.html", title="FileStorage", subtitle="A Decentralized Network for File Storage/Sharing", node_address=ADDR, request_tx=request_tx)

@app.route("/submit", methods=["POST"])
def submit():
    user = request.form["user"]
    up_file = request.files["v_file"]
    filename = secure_filename(up_file.filename)
    up_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    files[filename] = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file_stats = os.stat(files[filename]).st_size
    post_object = {
        "user": user,
        "v_file": filename,
        "file_data": str(up_file.stream.read()),
        "file_size": file_stats
    }
    address = "{0}/new_transaction".format(ADDR)
    requests.post(address, json=post_object)
    return redirect("/")

@app.route("/submit/<string:variable>", methods=["GET"])
def download_file(variable):
    p = files.get(variable)
    return send_file(p, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
