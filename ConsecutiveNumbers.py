#Author-Tim Fonshell
#Description-Create a scetch with consecutive numbers along a path.

# Attribution:
# Icon:
# For example: books, clothing, flyers, posters, invitations, publicity, etc.

# For example: 'image: Flaticon.com'. This cover has been designed using resources from Flaticon.com

import adsk.core, adsk.fusion, adsk.cam, traceback
import sys
import os
import math


handlers = []
selectedEdges = []
_angelCommandInput = adsk.core.AngleValueCommandInput.cast(None)

# Event handler for the commandCreated
class ConsNumberCommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
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
            # TODO: Add prefix and postfix
            # TODO: align text left, right, center

            # Global variables
            global _angelCommandInput

            # Chain definition
            chainGroupCmdInput = inputs.addGroupCommandInput("chainGroupCmdInputId", "Numberchain")
            chainGroupCmdInput.isExpanded = True
            chainGroupChildren = chainGroupCmdInput.children

            numbersStart = chainGroupChildren.addIntegerSpinnerCommandInput("numberStartIntSpinner", "Start Number", -2147483648, 2147483647, 1, 1)
            numbersEnd = chainGroupChildren.addIntegerSpinnerCommandInput("numberEndIntSpinner", "End Number", -2147483648, 2147483647, 1, 4)
            numbersSteps = chainGroupChildren.addIntegerSpinnerCommandInput("numberStepIntSpinner", "Steps", -2147483648, 2147483647, 1, 1)
            _angelCommandInput = chainGroupChildren.addAngleValueCommandInput("angleValue", "Angle", adsk.core.ValueInput.createByString("0 degree"))
            _angelCommandInput.hasMaximumValue = False
            _angelCommandInput.hasMinimumValue = False
            _angelCommandInput.setManipulator(adsk.core.Point3D.create(0,0,0), adsk.core.Vector3D.create(1,0,0), adsk.core.Vector3D.create(0,0,1))
            

            # Font definition
            fontGroupCmdInput = inputs.addGroupCommandInput("fontGroupCmdInputId", "Font")
            fontGroupCmdInput.isExpanded = False
            fontGroupChildren = fontGroupCmdInput.children

            numberHeight = fontGroupChildren.addFloatSpinnerCommandInput("numberHeightFloatSpinner", "Number Height", "mm", -2147483648, 2147483647, 1.0, 5)
            fontNameInput = fontGroupChildren.addTextBoxCommandInput("fontNameInput", "Font", "Arial", 1, False)
            boldButtonInput = fontGroupChildren.addBoolValueInput("BoldButtonInput", "Bold", True, 'resources/boldButton', True)

            # Geometry definition
            geometryGroupCmdInput = inputs.addGroupCommandInput("geometryGroupCmdInputId", "Geometry")
            geometryGroupCmdInput.isExpanded = True
            geometryGroupChildren = geometryGroupCmdInput.children

            sketchLineInput = geometryGroupChildren.addSelectionInput('sketchLine', 'Sketch Line', 'Select a sketch line to create the numbers on.')
            sketchLineInput.addSelectionFilter(adsk.core.SelectionCommandInput.SketchLines)
            sketchLineInput.setSelectionLimits(1)

            distanceValueInput = geometryGroupChildren.addDistanceValueCommandInput("extrusionDistanceInput", "Ditance", adsk.core.ValueInput.createByString("-1 mm"))
            distanceValueInput.setManipulator(adsk.core.Point3D.create(0,0,0), adsk.core.Vector3D.create(0,1,0))
            distanceValueInput.expression = '-1 mm'
            distanceValueInput.hasMinimumValue = False
            distanceValueInput.hasMaximumValue = False
            
            operationDropdownInput = geometryGroupChildren.addDropDownCommandInput("operationDropdownCmdInput", "Operation", adsk.core.DropDownStyles.LabeledIconDropDownStyle)
            operationDropDownItems = operationDropdownInput.listItems
            operationDropDownItems.add("New Body", True, '')
            operationDropDownItems.add("Join", False, '')
            operationDropDownItems.add("Cut", False, '')
            operationDropDownItems.add("Intersect", False, '')

            # Post- Prefix
            postPrefixGroupInput = inputs.addGroupCommandInput("PostPrefixGroupCmdInput", "Post- and Prefix")
            postPrefixGroupInput.isExpanded = False
            postPrefixGroupChildren = postPrefixGroupInput.children

            prefixInput = postPrefixGroupChildren.addTextBoxCommandInput("PrefixCommandInput", "Prefix", "", 1, False)
            postfixInput = postPrefixGroupChildren.addTextBoxCommandInput("PostfixCommandInput", "Postfix", "", 1, False)

        except Exception as e:
            numberStr = e
        
        # Connect to the execute event
        onExecute = ConsNumbersCommandExecuteHandler()
        cmd.execute.add(onExecute)
        handlers.append(onExecute)

        # Connect to OnDestroy handler
        onDestroy = ConsNumbersCommandDestroyHandler()
        cmd.destroy.add(onDestroy)
        handlers.append(onDestroy) 

        # Connect to select handler
        onSelect = ConsNumbersSelectHandler()
        cmd.select.add(onSelect)
        handlers.append(onSelect)   

        # Connect to unselect handler
        onUnSelect = ConsNumbersUnSelectHandler()
        cmd.unselect.add(onUnSelect)            
        handlers.append(onUnSelect) 

# Event handler for the execute event
class ConsNumbersCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        #eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
        eventArgs = adsk.core.CommandEventArgs.cast(args)
        app = adsk.core.Application.get()
        ui  = app.userInterface

        try:
            inputs = eventArgs.command.commandInputs

            minNumberInput = inputs.itemById('numberStartIntSpinner')
            minNumber = minNumberInput.value
            maxNumberInput = inputs.itemById('numberEndIntSpinner')
            maxNumber = maxNumberInput.value
            stepsInput = inputs.itemById('numberStepIntSpinner')
            steps = stepsInput.value
            angleInput = inputs.itemById('angleValue')
            angle = angleInput.value
            distanceInput = inputs.itemById('extrusionDistanceInput')
            distance = distanceInput.value
            numberHeightInput = inputs.itemById('numberHeightFloatSpinner')
            numberHeight = numberHeightInput.value
            fontInput = inputs.itemById('fontNameInput')
            font = fontInput.text
            operationInput = inputs.itemById('operationDropdownCmdInput')
            operation = operationInput.selectedItem.name
            boldInput = inputs.itemById('BoldButtonInput')
            bold = boldInput.value
            prefixInput = inputs.itemById("PrefixCommandInput")
            prefix = prefixInput.text
            postfixInput = inputs.itemById("PostfixCommandInput")
            postfix = postfixInput.text

            drawNumbers(minNumber, maxNumber, steps, angle, distance, numberHeight, font, operation, bold, prefix, postfix)
        except Exception as e:
            e = sys.exc_info()[0]
            ui.messageBox('FFFUUUUUUUCK!!!!!!!!!!!!!!!')

class ConsNumbersCommandDestroyHandler(adsk.core.CommandEventHandler):
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

class ConsNumbersSelectHandler(adsk.core.SelectionEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        app = adsk.core.Application.get()
        ui = app.userInterface
        global _angelCommandInput
        try:
            selectedEdge = adsk.fusion.SketchLine.cast(args.selection.entity)
            # selectedEdge = adsk.fusion.BRepEdge.cast(args.selection.entity) 
            if selectedEdge:
                selectedEdges.append(selectedEdge)
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class ConsNumbersUnSelectHandler(adsk.core.SelectionEventHandler):
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

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions

        # Create a button command definition.
        consNumbersButton = cmdDefs.addButtonDefinition('ConNumbersButtonDefID2', 
            'Consecutive Numbers', 
            'Creates a row of consecutive numbers on a line and extrudes them.', 
            './Resources/NumbersIcon')
        
        # Connect to the command created event.
        sampleCommandCreated = ConsNumberCommandCreatedEventHandler()
        consNumbersButton.commandCreated.add(sampleCommandCreated)
        handlers.append(sampleCommandCreated)

        # Get the ADD-INS panel in the model workspace
        # addInsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        solidCreatePanel = ui.allToolbarPanels.itemById('SolidCreatePanel')

        # Add the button to the bottom of the panel
        buttonControl = solidCreatePanel.controls.addCommand(consNumbersButton)

        # Prevent this module from being terminated when the script returns, because we are waiting for event handlers to fire.
        adsk.autoTerminate(False)
        
    except Exception as e:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Clean up the UI.
        cmdDef = ui.commandDefinitions.itemById('ConNumbersButtonDefID2')
        if cmdDef:
            cmdDef.deleteMe()
        
        solidPanel = ui.allToolbarPanels.itemById('SolidCreatePanel')
        cntrl = solidPanel.controls.itemById('ConNumbersButtonDefID2')
        if cntrl:
            cntrl.deleteMe()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def drawNumbers(minNumber, maxNumber, steps, angle, distance, numberHeight, font, operation, bold, prefix, postfix):
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
    # angleRad = angle % math.pi
    angleRad = angle
    textFlip = False
    # Angle adjustment to get the full range of rotation for text
    if angleRad == -math.pi:
        angleRad += math.pi
        textFlip = True
    if angleRad >= math.pi:
        angleRad -= math.pi
        textFlip = True
    # Angle calculation to align text angle to sketch line
    lineAngle = lineVector.angleTo(adsk.core.Vector3D.create(0,1,0))
    pathAngle = lineAngle + angleRad
    pathVector = adsk.core.Vector3D.create(0.1*math.cos(pathAngle), 0.1*math.sin(pathAngle), 0)


    # create points along line
    numberOfPoints = int((maxNumber - minNumber) / steps)
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
        textLine = lines.addByTwoPoints(currentStartVector.asPoint(), currentEndVector.asPoint())

        numberStr = str(iteration * steps + minNumber)
        if prefix != "":
            if prefix[-1] != " ":
                prefix = prefix + " "
        if postfix != "":
            if postfix[0] != " ":
                postfix = " " + postfix
        numberStr = prefix + numberStr + postfix
        
        textInput = skTexts.createInput2(numberStr, numberHeight)
        textInput.setAsAlongPath(textLine, False, adsk.core.HorizontalAlignments.CenterHorizontalAlignment, 0)
        textInput.isVerticalFlip = textFlip
        textInput.isHorizontalFlip = textFlip
        textInput.fontName = font
        if bold == True:
            textInput.textStyle = adsk.fusion.TextStyles.TextStyleBold
        try:
            skTexts.add(textInput)
        except:
            textInput.fontName = 'Arial'
            skTexts.add(textInput)
            
        sketchProfiles.add(skTexts.item(iteration))

    extrusionDistance = adsk.core.ValueInput.createByReal(distance)
    setDistance = adsk.fusion.DistanceExtentDefinition.create(extrusionDistance)
    
    # Dictionary for operation decision
    operationValue = {
        "New Body" : adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
        "Join" : adsk.fusion.FeatureOperations.JoinFeatureOperation,
        "Cut" : adsk.fusion.FeatureOperations.CutFeatureOperation,
        "Intersect" : adsk.fusion.FeatureOperations.IntersectFeatureOperation
    }

    extrudeInput = extrudes.createInput(sketchProfiles, operationValue[operation])
    extrudeInput.setOneSideExtent(setDistance, adsk.fusion.ExtentDirections.PositiveExtentDirection)
    # Get the extrusion body
    extrude1 = extrudes.add(extrudeInput)
    numbersBody = extrude1.bodies.item(0)
    numbersBody.name = "consNumbers"

    # Get the state of the extrusion
    health = extrude1.healthState
    if health == adsk.fusion.FeatureHealthStates.WarningFeatureHealthState or health == adsk.fusion.FeatureHealthStates.ErrorFeatureHealthState:
        message = extrude1.errorOrWarningMessage
    
    # Get the state of timeline object
    timeline = design.timeline
    timelineObj = timeline.item(timeline.count - 1)
    health = timelineObj.healthState
    message = timelineObj.errorOrWarningMessage