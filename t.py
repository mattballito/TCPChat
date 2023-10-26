class ChartGenerator(QObject):
    createChartWindow = Signal()

    def __init__(self, parent):
        super().__init__()

        # Get the parent QML item
        self.qml_item = parent

        # Expose the Python class to QML
        self.qml_item.setProperty("chartGenerator", self)

    @Slot()
    def createChartWindow(self):
        # Create a QML component dynamically
        component = QQmlComponent(self.qml_item.engine(), QUrl.fromLocalFile('ChartWindow.qml'))

        # Create an instance of the component
        chart_window_item = component.create()

        # Set properties or perform additional setup if needed
        # ...

        # Show the QML window
        chart_window_item.show()