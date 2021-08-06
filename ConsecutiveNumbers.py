#Author-Tim Fonshell
#Description-Create a scetch with consecutive numbers along a path.

import adsk.core, adsk.fusion, adsk.cam, traceback
import sys

handlers = []
selectedEdges = []

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

        # Prevent this module from being terminated when the script returns, because we are waiting for event handlers to fire.
        adsk.autoTerminate(False)
        
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

        sketchLineInput = inputs.addSelectionInput('sketchLine', 'Sketch Line', 'Select a sketch line to create the numbers on.')
        sketchLineInput.addSelectionFilter(adsk.core.SelectionCommandInput.SketchLines)
        sketchLineInput.setSelectionLimits(1)
        
        # Connect to the execute event
        onExecute = SampleCommandExecuteHandler()
        cmd.execute.add(onExecute)
        handlers.append(onExecute)

        # Connect to OnDestroy handler
        onDestroy = MyCommandDestroyHandler()
        cmd.destroy.add(onDestroy)
        handlers.append(onDestroy) 

        # Connect to select handler
        onSelect = MySelectHandler()
        cmd.select.add(onSelect)
        handlers.append(onSelect)   

        # Connect to unselect handler
        onUnSelect = MyUnSelectHandler()
        cmd.unselect.add(onUnSelect)            
        handlers.append(onUnSelect) 

# Event handler for the execute event
class SampleCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        #eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
        eventArgs = adsk.core.CommandEventArgs.cast(args)
        app = adsk.core.Application.get()
        ui  = app.userInterface

        try:
            inputs = eventArgs.command.commandInputs

            selectedPath = inputs.itemById('sketchLine')
            minNumber = inputs.itemById('numbersStart')
            maxNumber = inputs.itemById('numbersEnd')
            steps = inputs.itemById('numbersSteps')

            selectedPath

            drawNumbers(selectedPath, minNumber, maxNumber, steps)
        except Exception as e:
            e = sys.exc_info()[0]
            ui.messageBox('FFFUUUUUUUCK!!!!!!!!!!!!!!!')

class MyCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        app = adsk.core.Application.get()
        ui = app.userInterface
        try:
            # when the command is done, terminate the script
            # this will release all globals which will remove all event handlers
            # adsk.terminate()
            selectedEdges.clear()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class MySelectHandler(adsk.core.SelectionEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        app = adsk.core.Application.get()
        ui = app.userInterface
        try:
            selectedEdge = adsk.fusion.SketchLine.cast(args.selection.entity)
            # selectedEdge = adsk.fusion.BRepEdge.cast(args.selection.entity) 
            if selectedEdge:
                selectedEdges.append(selectedEdge)
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class MyUnSelectHandler(adsk.core.SelectionEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        app = adsk.core.Application.get()
        ui = app.userInterface
        try:
            # selectedEdge = adsk.fusion.BRepEdge.cast(args.selection.entity) 
            selectedEdge = adsk.fusion.SketchLine.cast(args.selection.entity)
            if selectedEdge:
                selectedEdges.remove(selectedEdge)
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

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

    design = app.activeProduct
    #doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)

    # Get the root component of the active design.
    rootComp = design.rootComponent

    sketchLine = adsk.fusion.SketchLine.cast(selectedEdges[0])

    sketch = sketchLine.parentSketch

    points = sketch.sketchPoints
    point = adsk.core.Point3D.create(0,0,0)
    points.add(point)
    lines = sketch.sketchCurves.sketchLines

    # rectangles = sketch.sketchCurves.sketchLines.addCenterPointRectangle(sketchLine.startSketchPoint, point)
    rectangle = lines.addCenterPointRectangle(point, sketchLine.endSketchPoint)



    # sketches = rootComp.sketches

    # xyPlane = rootComp.xYConstructionPlane

    # sketch = sketches.add(xyPlane)

    # circles = sketch.sketchCurves.sketchCircles
    # circle1 = circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 2)