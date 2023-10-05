import QtQuick 2.15
import QtQuick.Controls 2.15
import QtCharts 2.15

function showGraph(text) {
    // Create a simple line graph
    var chartView = Qt.createQmlObject('import QtCharts 2.15; ChartView {}', parent);
    chartView.title = "Sample Line Chart";

    var lineSeries = Qt.createQmlObject('import QtCharts 2.15; LineSeries {}', chartView);
    lineSeries.name = "Sample Series";
    lineSeries.append(0, 1);
    lineSeries.append(1, 3);
    lineSeries.append(2, 2);
    // Add more points as needed

    var axisX = Qt.createQmlObject('import QtCharts 2.15; ValueAxis {}', chartView);
    axisX.min = 0;
    axisX.max = 4;
    axisX.labelFormat = "%.0f";
    axisX.titleText = "X Axis";

    var axisY = Qt.createQmlObject('import QtCharts 2.15; ValueAxis {}', chartView);
    axisY.min = 0;
    axisY.max = 5;
    axisY.labelFormat = "%.0f";
    axisY.titleText = "Y Axis";

    chartView.addSeries(lineSeries);
    chartView.addAxis(axisX, Qt.AlignBottom);
    chartView.addAxis(axisY, Qt.AlignLeft);

    // Adjust chart position
    chartView.x = calTextField.mapToItem(parent, 0, 0).x;
    chartView.y = calTextField.mapToItem(parent, 0, 0).y + calTextField.height;

    // Show the chart
    chartView.show();
}

// Define a model for the chart data
    ListModel {
        id: chartModel
        ListElement { x: 1; y: 2 }
        ListElement { x: 2; y: 4 }
        ListElement { x: 3; y: 1 }
        // Add more data points as needed
    }

    // Create a LineSeries for the chart
    LineSeries {
        id: lineSeries
        name: "Line Series"
        XYPoint { x: 1; y: 2 }
        XYPoint { x: 2; y: 4 }
        XYPoint { x: 3; y: 1 }
        // Add more points as needed
    }

    ChartView {
        id: chartView
        title: "Line Chart"
        anchors.fill: parent
        antialiasing: true
        legend.visible: true

        ValueAxis {
            id: axisX
            min: 0
            max: 4
            labelFormat: "%.0f"
            titleText: "X Axis"
        }

        ValueAxis {
            id: axisY
            min: 0
            max: 5
            labelFormat: "%.0f"
            titleText: "Y Axis"
        }

        TapHandler {
            acceptedButtons: Qt.RightButton
            onTapped: {
                console.log("Hello World!");
                regressionPlotMenu.popup()
            }
        }
    }

    Menu {
        id: regressionPlotMenu
        MenuItem {
            text: "Show Line Chart"
            onClicked: {
                // Clear existing data in the chart
                lineSeries.clear();

                // Add data from the model to the chart
                for (var i = 0; i < chartModel.count; ++i) {
                    lineSeries.append(chartModel.get(i).x, chartModel.get(i).y);
                }

                // Assign the series to the chart
                chartView.chart = lineSeries;

                // Show the chart
                chartView.show();
            }
        }
    }







ChartView {
        id: chartView
        visible: false // Initially hide the chart
        anchors.top: textField.bottom
        width: parent.width
        height: parent.height - textField.height // Adjust height to accommodate the TextField
        antialiasing: true
        legend.visible: true

        ValueAxis {
            id: axisX
            min: 0
            max: 4
            labelFormat: "%.0f"
            titleText: "X Axis"
        }

        ValueAxis {
            id: axisY
            min: 0
            max: 5
            labelFormat: "%.0f"
            titleText: "Y Axis"
        }

        LineSeries {
            id: lineSeries
            name: "Line Series"
            // Add more points as needed
        }
    }