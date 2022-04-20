class Gauge {
    constructor(server) {
        console.log("Gauge constructor, server = " + server);
        this.server = server;

        this.ByteBlowerGraphsApp = {}; // global variable
        this.ByteBlowerGraphsApp.graphCounter = 0; // let's keep track of the graphs added to the page
        this.ByteBlowerGraphsApp.graphThreads = {}; // let's keep track of the graphs updater threads that are running in the background
    }

    /**
     * Adds a graph to class
     * @param stream = Trunk for stream
     * @param container_name = Container id of container to which the graph needs to be appended. (Containers are created in gauge.html)
     * @param graph_name = upstream or downstream
     */
    addGraph(stream, container_name, graph_name) {

        const prevDiv = document.getElementById(container_name);

        console.log("stream = " + stream);

        // the new div will contain all new elements (textfields, buttons and chart)
        const newDiv = document.createElement("div");
        newDiv.setAttribute("id", "container" + this.ByteBlowerGraphsApp.graphCounter);
        newDiv.setAttribute("style", "width: 100%;");
        // prevDiv.appendChild(newDiv);

        // horizontal helper layout to display the textfields and buttons
        const optionsDiv = document.createElement("div");
        optionsDiv.setAttribute("align", "center");
        optionsDiv.setAttribute("horizontal", "");
        optionsDiv.setAttribute("layout", "");
        newDiv.appendChild(optionsDiv);


        const chart_name = "chart" + this.ByteBlowerGraphsApp.graphCounter;

        // the div that will contain the highcharts chart
        const chartDiv = document.createElement("div");
        // chartDiv.setAttribute("id", "chart" + this.ByteBlowerGraphsApp.graphCounter);
        chartDiv.setAttribute("id", chart_name);
        chartDiv.setAttribute("style", "min-width: 310px; height: 400px; margin: 0 auto");
        newDiv.appendChild(chartDiv);

        prevDiv.appendChild(newDiv);

        const gaugeOptions = {
            chart: {
				type: 'solidgauge',
				height: '75%'
			},

            title: null,

            pane: {
                center: ['50%', '60%'],
                size: '95%',
                startAngle: -90,
                endAngle: 90,
                background: {
                    backgroundColor:
                        Highcharts.defaultOptions.legend.backgroundColor || '#f7f7f7',
                    innerRadius: '60%',
                    outerRadius: '110%',
                    shape: 'arc'
                }
            },

            exporting: {
                enabled: false
            },

            tooltip: {
                enabled: false
            },

            // the value axis
            yAxis: {
                lineWidth: 0,
                title: {
                    y: 20
                },
                labels: {
                    y: 16
                },
				tickAmount: 2,
				tickWidth: 0,
				minorTickInterval: null
            },

            plotOptions: {
                solidgauge: {
                    dataLabels: {
                        y: 5,
                        borderWidth: 0,
                        useHTML: true
                    },
					linecap: 'round',
					stickyTracking: true,
					rounded: false
                }
            }
        };

        // TODO: Max needs to be adjustable
        Highcharts.chart(chart_name, Highcharts.merge(gaugeOptions, {
            yAxis: {
                min: 0,
                max: 1,
                title: {
                    text: graph_name
                }
            },

            credits: {
                enabled: false
            },

            series: [{
                name: 'Max Speed',
                data: [{
					color: '#01C36B',
					radius: '110%',
					innerRadius: '85%',
					y: 0
				}],
                dataLabels: {
                    format:
                        '<div style="text-align:center">' +
                        '<span style="font-size:25px">{y}</span><br/>' +
                        '<span style="font-size:12px;opacity:0.4">Gb/s</span>' +
                        '</div>'
                },
                tooltip: {
                    valueSuffix: ' Gb/s'
                }
            },
			{
                name: 'Current Speed',
                data: [{
                    color: '#169FDB',
					radius: '84%',
					innerRadius: '60%',
					y: 0
				}],
                dataLabels: {
                    format:
                        '<div style="text-align:center">' +
                        '<span style="font-size:25px">{y}</span><br/>' +
                        '<span style="font-size:12px;opacity:0.4">Gb/s</span>' +
                        '</div>'
                },
                tooltip: {
                    valueSuffix: ' Gb/s'
                }
            }]
        }));


        this.startGraph(chart_name, stream);
        this.ByteBlowerGraphsApp.graphCounter++;
    }

    startGraph(chart_name, stream) {
        console.log("start graph");

        const chart = $("#" + chart_name).highcharts();
		const MAX_HISTORY_SECS = 10;

        let seriesMax = chart.series[0];
		let seriesCurrent = chart.series[1];
        let pointMax = seriesMax.points[0];
		let pointCurrent = seriesCurrent.points[0];
        let valueHistory = Array(MAX_HISTORY_SECS).fill(0);
		let valueHistoryPointer = 0;


        const server_name = this.server;
        console.log("server name = " + server_name);

        // set up the updating of the chart each second (1000 ms)
        this.ByteBlowerGraphsApp.graphThreads["" + this.ByteBlowerGraphsApp.graphCounter] = setInterval(function () {

            let y = 0;
            // we fetch the latest update from the ByteBlower server through a python script that is running in the background
            // the python script is accessed through a REST API at port 5000
            $.getJSON('/data.json/' + server_name + '/' + stream, function (data) {
                console.log("fetched data: " + data);
                y = Math.round(data/1000 *100)/100;
				valueHistory[valueHistoryPointer] = y;
                valueHistoryPointer = (valueHistoryPointer + 1) % MAX_HISTORY_SECS

				pointMax.update(Math.max(...valueHistory));
				pointCurrent.update(y);
            });

        }, 1000);
    }
}