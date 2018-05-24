## Needed for python2 / python3 print function compatibility
from __future__ import print_function
from flask import Flask, render_template, request
import sqlite3
import json
from random import randint
import webbrowser
import thread
import time

# import the ByteBlower module
import byteblowerll.byteblower as byteblower

# the Flask library is used to create a REST-alike API 
app = Flask(__name__)
byteblower_instance = byteblower.ByteBlower.InstanceGet() 
# global variable that keeps track of the ByteBlower server objects that were created (to avoid doing this multiple times)
server_cache = {}
# global variable that keeps track of the ByteBlower result snapshot objects that were created (to avoid doing this multiple times)
snapshot_cache = {}
# global variable that keeps track of the previous refresh timestamp for each result snapshot (to calculate differences and mbps)
snapshot_timestamp_cache = {}
# global variable that keeps track of the previous byte count for each result snapshot (to calculate differences and mbps)
snapshot_bytecount_cache = {}

# this is the call that is done by the highcharts charts to get new data for their graph
# the url contains the ByteBlower server address and interface(s) the graph is for 
@app.route("/data.json/<serverAddress>/<interfaces>")
def data(serverAddress,interfaces):
    try:
        if serverAddress not in server_cache:
            print("Creating BB server: {}".format(serverAddress))
            server = byteblower_instance.ServerAdd(str(serverAddress))
            server_cache[serverAddress] = server
        server = server_cache[serverAddress]
        print("Server found: {}".format(serverAddress))
        snapshots = []
        # a single graph can monitor a single interface (for example trunk-1-1) or the sum of multiple interfaces (for example trunk-1-1+trunk-1-2)
        for interface in interfaces.split("+"):
            if "{}-{}".format(serverAddress,interface) not in snapshot_cache:
                print("Creating BB port with trigger at interface {}".format(interface))
                port = server.PortCreate(str(interface))
                # add basic trigger to the port to start monitoring
                trigger = port.RxTriggerBasicAdd()
                # get the result snapshot object that we then can refresh everytime we need a new result
                trigger_snapshot = trigger.ResultGet()
                snapshot_cache["{}-{}".format(serverAddress,interface)] = trigger_snapshot
                snapshot_timestamp_cache[trigger_snapshot] = trigger_snapshot.RefreshTimestampGet()
                snapshot_bytecount_cache[trigger_snapshot] = trigger_snapshot.ByteCountGet()
            snapshot = snapshot_cache["{}-{}".format(serverAddress,interface)]
            print("Port snapshot found: {}".format(interface))
            snapshots.append(snapshot)
        mbps_total = 0.0;
        for snapshot in snapshots:
            # refresh all snapshots simultaneously
            snapshot.Refresh()
            # calculate the mbps since the last time this value was fetched
            byteCountDiff = (snapshot.ByteCountGet() - snapshot_bytecount_cache[snapshot])
            timeStampDiff = (snapshot.RefreshTimestampGet() - snapshot_timestamp_cache[snapshot])
            print("Timestamp diff = {}".format(timeStampDiff))
            mbps_total = mbps_total + byteCountDiff * 8.0 / timeStampDiff * 1e9 / 1e6
            snapshot_timestamp_cache[snapshot] = snapshot.RefreshTimestampGet()
            snapshot_bytecount_cache[snapshot] = snapshot.ByteCountGet()
        print("Throughput: {} Mbps".format(round(mbps_total,2)))
        # round the value to 2 decimals and return it
        return json.dumps(round(mbps_total,2))    
            
    except Exception as e:
        print("Unable to fetch data")
        print(e)
    return json.dumps(0.00)
 
@app.route("/graph")
def graph():
    # this allows to access the static page through the following url:
    # http://127.0.0.1:5000/graph
    # the html template (with the highcharts javascript) needs to be under the subdirectory templates/
    return render_template('graph.html')

# small trick to automatically start browser and show the correct page once the Flask webapp is running
def browserThread():
    time.sleep(3)
    # only works on Windows!
    chrome_path='C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
    try :
        webbrowser.get(chrome_path).open_new("127.0.0.1:5000/graph")
    except:
        print("Unable to start Chrome, using default browser instead...")
        webbrowser.open_new("127.0.0.1:5000/graph")
 
if __name__ == '__main__':
    # start background thread to open browser once the Flask webapp is started
    thread.start_new_thread(browserThread,())
    # start Flask webapp
    app.run(
    debug=True,
    threaded=True,
    host='0.0.0.0'
    )
    
    