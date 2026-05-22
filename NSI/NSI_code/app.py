from flask import Flask, render_template, send_from_directory, abort
import os

app = Flask(__name__)

def picking_scan():
    scans = os.listdir('scans')
    _ = 0

    scans.sort(reverse=True)

    selected_file:str = ""
    if len(scans) == 1:
        selected_file = scans[0]
    else:
        selected_file = scans[1]
    

    elements = selected_file.split("_")
    elements = selected_file.split('_')
    date = elements[2]
    time = elements[3].replace("-",":")
    pcd_points = elements[4][:-4] # getting rid of .png
    return selected_file, date, time, pcd_points





@app.route("/")
def index():
    file_name, date, time, pcd_points = picking_scan()
    return render_template("index.html", image_filename = file_name, date=date, time=time,pcd_points = pcd_points)

@app.route("/scans/<filename>")
def scans(filename):
    return send_from_directory("scans", filename)

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = 5001, debug = True)







