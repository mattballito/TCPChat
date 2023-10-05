import QtQuick 2.15
import QtQuick.Controls 2.15
import QtCharts 2.15

ApplicationWindow {
    visible: true
    width: 800
    height: 600

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

        // Assign the series to the chart
        series: [lineSeries]

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

                // Show the chart
                chartView.show();
            }
        }
    }
}
