#Author-Tim Fonshell
#Description-Create a scetch with consecutive numbers along a path.

import adsk.core, adsk.fusion, adsk.cam, traceback
import sys

handlers = []

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions

        # Create a button command definition.
        buttonSample = cmdDefs.addButtonDefinition('MyButtonDefId2', 
            'Python sample button', 
            'Sample button tolltip', 
            './Resources/Sample')
        
        # Connect to the command created event.
        sampleCommandCreated = sampleCommandCreatedEventHandler()
        buttonSample.commandCreated.add(sampleCommandCreated)
        handlers.append(sampleCommandCreated)

        # Get the ADD-INS panel in the model workspace
        addInsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')

        # Add the button to the bottom of the panel
        buttonControl = addInsPanel.controls.addCommand(buttonSample)
        
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the commandCreated
class sampleCommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
        cmd = eventArgs.command
        inputs = cmd.commandInputs

        # create commands
        numbersStart = inputs.addValueInput('numbersStart', 'First Number', '', adsk.core.ValueInput.createByReal(1))
        numbersEnd = inputs.addValueInput('numbersEnd', 'Last Number', '', adsk.core.ValueInput.createByReal(3))
        numbersSteps = inputs.addValueInput('numbersSteps', 'Steps', '', adsk.core.ValueInput.createByReal(1))
        #sketchLine = inputs.addSelectionInput('sketchLine', 'Sketch Line', 'Select a sketch line to create the numbers on.')
        
        # Connect to the execute event
        onExecute = SampleCommandExecuteHandler()
        cmd.execute.add(onExecute)
        handlers.append(onExecute)

# Event handler for the execute event
class SampleCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
        app = adsk.core.Application.get()
        ui  = app.userInterface

        try:
            inputs = eventArgs.command.commandInputs

            selectedPath = inputs.itemById('sketchLine')
            minNumber = inputs.itemById('numbersStart')
            maxNumber = inputs.itemById('numbersEnd')
            steps = inputs.itemById('numbersSteps')

            drawNumbers(selectedPath, minNumber, maxNumber, steps)
        except Exception as e:
            e = sys.exc_info()[0]
            ui.messageBox(e.args[0])

def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Clean up the UI.
        cmdDef = ui.commandDefinitions.itemById('MyButtonDefId2')
        if cmdDef:
            cmdDef.deleteMe()
        
        addinsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        cntrl = addinsPanel.controls.itemById('MyButtonDefId2')
        if cntrl:
            cntrl.deleteMe()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def drawNumbers(selectedPath, minNumber, maxNumber, steps):
    # Code to react to the event
    app = adsk.core.Application.get()
    ui = app.userInterface
    ui.messageBox('Test button clicked')

    design = app.activeProduct
    #doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)

    # Get the root component of the active design.
    rootComp = design.rootComponent

    testSketch = selectedPath.parentSketch

    sketchPoints = testSketch.sketchPoints

    pointsList = []

    startPoint = selectedPath.startSketchPoint



    # sketches = rootComp.sketches

    # xyPlane = rootComp.xYConstructionPlane

    # sketch = sketches.add(xyPlane)

    # circles = sketch.sketchCurves.sketchCircles
    # circle1 = circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 2)