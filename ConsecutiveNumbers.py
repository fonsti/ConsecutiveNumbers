#Author-Tim Fonshell
#Description-Create a scetch with consecutive numbers along a path.

import adsk.core, adsk.fusion, adsk.cam, traceback
import sys
import os
import math


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

        app = adsk.core.Application.get()
        ui  = app.userInterface

        # create input commands
        try:
            numbersStart = inputs.addIntegerSpinnerCommandInput("numberStartIntSpinner", "Start Number", -2147483648, 2147483647, 1, 1)
            numbersEnd = inputs.addIntegerSpinnerCommandInput("numberEndIntSpinner", "End Number", -2147483648, 2147483647, 1, 4)
            numbersSteps = inputs.addIntegerSpinnerCommandInput("numberStepIntSpinner", "Steps", -2147483648, 2147483647, 1, 1)
            numberHeight = inputs.addFloatSpinnerCommandInput("numberHeightFloatSpinner", "Number Height", "mm", -2147483648, 2147483647, 1.0, 5)
            setAngle = inputs.addAngleValueCommandInput("angleValue", "Angle", adsk.core.ValueInput.createByString("90 degree"))
            setAngle.hasMaximumValue = False
            setAngle.hasMinimumValue = False
            setAngle.setManipulator(adsk.core.Point3D.create(0,0,0), adsk.core.Vector3D.create(1,0,0), adsk.core.Vector3D.create(0,0,1))
            distanceValueInput = inputs.addDistanceValueCommandInput("extrusionDistanceInput", "Ditance", adsk.core.ValueInput.createByString("-1 mm"))
            distanceValueInput.setManipulator(adsk.core.Point3D.create(0,0,0), adsk.core.Vector3D.create(0,1,0))
            distanceValueInput.expression = '-1 mm'
            distanceValueInput.hasMinimumValue = False
            distanceValueInput.hasMaximumValue = False

            textBoxInput = inputs.addTextBoxCommandInput("fontNameInput", "Font", "Arial", 1, False)

            # dropDownInputFonts = inputs.addDropDownCommandInput("selectedFont", "Font", adsk.core.DropDownStyles.TextListDropDownStyle)
            # dropDownFontsItems = dropDownInputFonts.listItems
            # availableFonts = os.listdir(r'C:\\Windows\\fonts')
            # for item in availableFonts:
            #     fontName = os.path.splitext(item)[0]
            #     fontExtension = os.path.splitext(item)[1]
            #     dropDownFontsItems.add(fontName, False, '')

            sketchLineInput = inputs.addSelectionInput('sketchLine', 'Sketch Line', 'Select a sketch line to create the numbers on.')
            sketchLineInput.addSelectionFilter(adsk.core.SelectionCommandInput.SketchLines)
            sketchLineInput.setSelectionLimits(1)
        except Exception as e:
            test = e
        
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

            minNumber = inputs.itemById('numberStartIntSpinner')
            maxNumber = inputs.itemById('numberEndIntSpinner')
            steps = inputs.itemById('numberStepIntSpinner')
            angle = inputs.itemById('angleValue')
            distance = inputs.itemById('extrusionDistanceInput')
            numberHeight = inputs.itemById('numberHeightFloatSpinner')
            fontInput = inputs.itemById('fontNameInput')

            drawNumbers(minNumber, maxNumber, steps, angle, distance, numberHeight, fontInput)
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


def drawNumbers(minNumber, maxNumber, steps, angle, distance, numberHeight, fontInput):
    # Code to react to the event
    app = adsk.core.Application.get()
    ui = app.userInterface

    design = app.activeProduct

    # Get the root component of the active design.
    rootComp = design.rootComponent

    # get selected sketch line, and other objects
    sketchLine = adsk.fusion.SketchLine.cast(selectedEdges[0])
    sketch = sketchLine.parentSketch
    points = sketch.sketchPoints
    lines = sketch.sketchCurves.sketchLines

    # define the start and end points of the operation
    startVector = sketchLine.startSketchPoint.geometry.asVector()
    endVector = sketchLine.endSketchPoint.geometry.asVector()
    lineVector = endVector.copy()
    lineVector.subtract(startVector)

    # calulate vector for text path
    angleRad = angle.value
    angleRad %= math.pi*2
    textFlip = False
    if angleRad <= math.pi/(-2):
        angleRad += math.pi
        textFlip = True
    if angleRad > math.pi/2:
        angleRad -= math.pi
        textFlip = True
    lineAngle = lineVector.angleTo(adsk.core.Vector3D.create(0,1,0))
    pathAngle = lineAngle + angleRad
    pathVector = adsk.core.Vector3D.create(0.1*math.cos(pathAngle), 0.1*math.sin(pathAngle), 0)


    # create points along line
    numberOfPoints = int((maxNumber.value - minNumber.value) / steps.value)
    #numberOfPoints = 4-1
    currentPointVector = startVector.copy()
    partLineVector = lineVector.copy()
    partLineVector.scaleBy(1/numberOfPoints)
    pointsOnLine = []
    pointsOnLine.append(adsk.core.Vector3D.asPoint(startVector))
    for iteration in range(0, numberOfPoints):
        currentPointVector.add(partLineVector)
        point = adsk.core.Vector3D.asPoint(currentPointVector)
        pointsOnLine.append(point)
        points.add(point)

    # create paths at angel through points
    skTexts = sketch.sketchTexts
    extrudes = rootComp.features.extrudeFeatures
    prof = sketch.profiles
    sketchProfiles = adsk.core.ObjectCollection.create()
    for iteration in range(0, len(pointsOnLine)):
        currentPointVector = pointsOnLine[iteration].asVector()
        currentStartVector = currentPointVector.copy()
        currentStartVector.add(pathVector)
        currentEndVector = currentPointVector.copy()
        currentEndVector.subtract(pathVector)
        newLine = lines.addByTwoPoints(currentStartVector.asPoint(), currentEndVector.asPoint())

        test = str(iteration * steps.value + minNumber.value)
        input = skTexts.createInput2(test, numberHeight.value)
        input.setAsAlongPath(newLine, False, adsk.core.HorizontalAlignments.CenterHorizontalAlignment, 0)
        input.isVerticalFlip = textFlip
        input.isHorizontalFlip = textFlip
        input.fontName = fontInput.text
        input.textStyle = adsk.fusion.TextStyles.TextStyleBold
        try:
            skTexts.add(input)
        except:
            input.fontName = 'Arial'
            skTexts.add(input)
            
        sketchProfiles.add(skTexts.item(iteration))

    mm1 = adsk.core.ValueInput.createByReal(distance.value)
    setDistance = adsk.fusion.DistanceExtentDefinition.create(mm1)
    # extrude1 = extrudes.addSimple(skTexts.item(iteration), distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)   
    extrudeInput = extrudes.createInput(sketchProfiles, adsk.fusion.FeatureOperations.CutFeatureOperation)
    extrudeInput.setOneSideExtent(setDistance, adsk.fusion.ExtentDirections.PositiveExtentDirection)
    # Get the extrusion body
    extrude1 = extrudes.add(extrudeInput)
    body1 = extrude1.bodies.item(0)
    body1.name = "consNumbers"

    # Get the state of the extrusion
    health = extrude1.healthState
    if health == adsk.fusion.FeatureHealthStates.WarningFeatureHealthState or health == adsk.fusion.FeatureHealthStates.ErrorFeatureHealthState:
        message = extrude1.errorOrWarningMessage
    
    # Get the state of timeline object
    timeline = design.timeline
    timelineObj = timeline.item(timeline.count - 1)
    health = timelineObj.healthState
    message = timelineObj.errorOrWarningMessage