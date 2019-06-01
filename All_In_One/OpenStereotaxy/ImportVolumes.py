from __main__ import vtk, qt, ctk, slicer

# ================== SCNI_SurgeryPlanner ====================
# This Slicer module is for
#

class SurgeryPlanner
    def __init__(self, parent):
        parent.title = 'SCNI_SurgeryPlanner'
        parent.contributors = ['Aidan Murphy (NIH)']
        parent.helpText = "Import subject volumes"
        self.parent = parent


# SurgeryPlannerWidget

class SurgeryPlannerWidget:
    def __init__(self, parent = None):
        if not parent:
            self.parent = slicer.qMRMLWidget()
            self.parent.setLayout(qt.QVBoxLayout())
            self.parent.setMRMLScene(slicer.mrmlScene)
        else:
            self.parent = parent
            self.layout = self.parent.layout()
        if not parent:
            self.setup()
            self.parent.show()

    def setup(self):
        # Instantiate and connect widgets

        # Collapsable button
        dummyCollapsableButton = ctk.ctkCollapsableButton()
        dummyCollapsableButton.text = "A collapsable button"
        self.layout.addWidget(dummyCollapsableButton)

        # Layout within the dummy collapsable button
        dummyFormLayout = qt.QFormLayout(dummyCollapsableButton)

        # HellowWorld button
        helloWorldButton = qt.QPushButton("Hello world")
        helloWorldButton.toolTip = "Print 'Hello world' in standard ouput."
        sampleFormLayout.addWidget(helloWorldButton)
        helloWorldButton.connect('clicked(bool)', self.onHelloWorldButtonClicked)

        # Add vertical spacer
         self.layout.addStretch(1)
         # Set local var as instance attribute
         self.helloWorldButton = helloWorldButton

def onHelloWorldButtonClicked(self):
        print "Hello World !"
        qt.QMessageBox.information(slicer.util.mainWindow(), 'Slicer Python', 'Hellow World!')