## Needed for python2 / python3 print function compatibility
from __future__ import print_function
from flask import Flask, render_template, request, url_for
import json
from random import randint
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
def data(serverAddress, interfaces):
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
            if "{}-{}".format(serverAddress, interface) not in snapshot_cache:
                print("Creating BB port with trigger at interface {}".format(interface))
                port = server.PortCreate(str(interface))
                # add basic trigger to the port to start monitoring
                trigger = port.RxTriggerBasicAdd()
                # get the result snapshot object that we then can refresh everytime we need a new result
                trigger_snapshot = trigger.ResultGet()
                snapshot_cache["{}-{}".format(serverAddress, interface)] = trigger_snapshot
                snapshot_timestamp_cache[trigger_snapshot] = trigger_snapshot.RefreshTimestampGet()
                snapshot_bytecount_cache[trigger_snapshot] = trigger_snapshot.ByteCountGet()
            snapshot = snapshot_cache["{}-{}".format(serverAddress, interface)]
            print("Port snapshot found: {}".format(interface))
            snapshots.append(snapshot)
        mbps_total = 0.0

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
        print("Throughput: {} Mbps".format(round(mbps_total, 2)))
        # round the value to 2 decimals and return it
        return json.dumps(round(mbps_total, 2))

    except Exception as e:
        print("Unable to fetch data")
        print(e)
    return json.dumps(0.00)


@app.route("/home")
def home():
    # this allows to access the static page through the following url:
    # http://127.0.0.1:5000/graph
    # the html template (with the highcharts javascript) needs to be under the subdirectory templates/
    # return render_template('home.html')
    return render_template('excentis.html', template='home.html')


@app.route("/config_test", methods=['POST', 'GET'])
def config_test():
    # this allows to access the static page through the following url:
    # http://127.0.0.1:5000/test
    # the html template (with the highcharts javascript) needs to be under the subdirectory templates/
    if request.method == 'POST':
        serverAddress = request.form['server']
        try:
            if serverAddress not in server_cache:
                print("Creating BB server: {}".format(serverAddress))
                server = byteblower_instance.ServerAdd(str(serverAddress))
                server_cache[serverAddress] = server
            server = server_cache[serverAddress]
            print("Server found: {}".format(serverAddress))
            interfaceNames = server.InterfaceNamesGet()
            interfaces = []
            for interfaceName in interfaceNames:
                interfaces.append("{}".format(interfaceName))
            print("Interfaces found: {}".format(interfaces))
            return render_template('excentis.html', template='config_test.html', server=serverAddress,
                                   interfaces=interfaces)
        except Exception as e:
            print("Unable to fetch data")
            print(e)
    return render_template('home.html')


@app.route("/test/<server>", methods=['POST', 'GET'])
def test(server):
    # this allows to access the static page through the following url:
    # http://127.0.0.1:5000/test
    # the html template (with the highcharts javascript) needs to be under the subdirectory templates/
    if request.method == 'POST':
        # upstream and downstream settings for the three tests
        title1 = request.form['title1']
        print("title1 : {}".format(title1))
        up1 = request.form['up1']
        down1 = request.form['down1']

        title2 = request.form['title2']
        print("title2 : {}".format(title2))
        up2 = request.form['up2']
        down2 = request.form['down2']

        title3 = request.form['title3']
        print("title3 : {}".format(title3))
        up3 = request.form['up3']
        down3 = request.form['down3']

        # return render_template('gauge.html',server=server, interface=interface)ss
        return render_template('excentis.html',
                               template='gauge.html',
                               server=server,
                               title1=title1,
                               up1=up1,
                               down1=down1,
                               title2=title2,
                               up2=up2,
                               down2=down2,
                               title3=title3,
                               up3=up3,
                               down3=down3)

    return render_template('home.html')


if __name__ == '__main__':
    # start Flask webapp
    app.run(
        debug=True,
        threaded=True,
        host='0.0.0.0',
        port=5000
    )
