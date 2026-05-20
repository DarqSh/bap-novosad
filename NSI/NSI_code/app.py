from flask import Flask, render_template, send_from_directory, abort
import os

app = Flask(__name__)

def picking_scan():
    scans_files = os.listdir('scans')
    _ = 0
    photo_found:bool = False
    for filename in scans_files:
        if filename.startswith('latest_scan'):
            photo_found = True
            break
        _ += 1
    if photo_found == False:
        print("latest_scan wasn't found")
        exit # how to end program here
    file_name = scans_files[_]
    elements = file_name.split('_')
    date = elements[2]
    time = elements[3].replace("-",":")
    pcd_points = elements[4][:-4] # getting rid of .png
    return file_name, date, time, pcd_points





@app.route("/")
def index():
    file_name, date, time, pcd_points = picking_scan()
    return render_template("index.html", image_filename = file_name, date=date, time=time,pcd_points = pcd_points)

@app.route("/scans/<filename>")
def scans(filename):
    return send_from_directory("scans", filename)

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = 5001, debug = True)







