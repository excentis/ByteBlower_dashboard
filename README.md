# ByteBlower_dashboard
A quick-and-dirty web-based dashboard showing live graphs of each ByteBlower interface in our lab

This is example code to build a dashboard showing live RX-graphs of each ByteBlower Interface. You can dynamically add graphs in the WebUI. This dashboard is created by combining the ByteBlower Python API and some python libraries and frameworks.

## Pre-requisites

* Python 2.7
** Flask
* ByteBlower Python API
* ByteBlower Server


ByteBlower Python API can be download from following location: [ByteBlower Setup page](http://setup.byteblower.com)

## Run

Start the python code with following command:

```
python web.py
```
Open a browser to following location: http://127.0.0.1:5000/graph

## Usage
* Click the button to add a Graph
* Specify the server ( e.g. byteblower.example.com )
* Specify the interface ( e.g. trunk-1-1 )

To aggregate the traffic of interfaces you can use following syntax ( no spaces! between the interfaces )
```
trunk-1-1+trunk-1-2
```
