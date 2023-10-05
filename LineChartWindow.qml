import QtQuick 2.15
import QtQuick.Controls 2.15
import QtCharts 2.15

Window {
    visible: true
    width: 400
    height: 300

    ChartView {
        anchors.fill: parent
        antialiasing: true

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
            name: "Sample Series"
            // Sample data points
            XYPoint { x: 0; y: 1 }
            XYPoint { x: 1; y: 3 }
            XYPoint { x: 2; y: 2 }
            // Add more points as needed
        }
    }
}
