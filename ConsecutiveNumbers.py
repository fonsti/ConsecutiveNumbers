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

# Dictionary for operation decision
operationValues = {
    "New Body" : adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    "Join" : adsk.fusion.FeatureOperations.JoinFeatureOperation,
    "Cut" : adsk.fusion.FeatureOperations.CutFeatureOperation,
    "Intersect" : adsk.fusion.FeatureOperations.IntersectFeatureOperation
}

# Dictionary for alignmen values
alignmentValues = {
    "Left" : adsk.core.HorizontalAlignments.LeftHorizontalAlignment,
    "Right" : adsk.core.HorizontalAlignments.RightHorizontalAlignment,
    "Center" : adsk.core.HorizontalAlignments.CenterHorizontalAlignment
}

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
            # TODO: protect against reverse numbers
            # TODO: save parameters for next use

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

            alignmentDropDownInput = fontGroupChildren.addDropDownCommandInput("AlignmentDropDownInput", "Text Alignment", adsk.core.DropDownStyles.LabeledIconDropDownStyle)
            alignmentDropdownItems = alignmentDropDownInput.listItems
            alignmentDropdownItems.add("Left", False, '')
            alignmentDropdownItems.add("Right", False, '')
            alignmentDropdownItems.add("Center", True, '')
            
            onPathDropdownInput = fontGroupChildren.addDropDownCommandInput("onPathDropdownInput", "On Path", adsk.core.DropDownStyles.LabeledIconDropDownStyle)
            onPathDropDownItems = onPathDropdownInput.listItems
            onPathDropDownItems.add("On Top", True, '')
            onPathDropDownItems.add("Below", False, '')

            # Geometry definition
            geometryGroupCmdInput = inputs.addGroupCommandInput("geometryGroupCmdInputId", "Geometry")
            geometryGroupCmdInput.isExpanded = True
            geometryGroupChildren = geometryGroupCmdInput.children

            sketchLineInput = geometryGroupChildren.addSelectionInput('sketchLine', 'Sketch Line', 'Select a sketch line to create the numbers on.')
            sketchLineInput.addSelectionFilter(adsk.core.SelectionCommandInput.SketchLines)
            sketchLineInput.addSelectionFilter(adsk.core.SelectionCommandInput.SketchCurves)
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
            alignmentInput = inputs.itemById("AlignmentDropDownInput")
            alignment = alignmentInput.selectedItem.name
            onPathInput = inputs.itemById("onPathDropdownInput")
            onPath = onPathInput.selectedItem.name

            drawNumbers(minNumber, maxNumber, steps, angle, distance, numberHeight, font, operation, bold, prefix, postfix, alignment, onPath)
        except Exception as e:
            e = sys.exc_info()[0]
            # message box showing exception
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
            #ui.messageBox('An Error has Occurred')

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
            selectedEdge = adsk.fusion.SketchArc.cast(args.selection.entity)
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


def drawNumbers(minNumber, maxNumber, steps, angle, distance, numberHeight, font, operation, bold, prefix, postfix, alignment, onPath):

    app = adsk.core.Application.get()
    ui = app.userInterface

    design = app.activeProduct

    # Get the root component of the active design.
    rootComp = design.rootComponent
    
    # identify which kind of edge is used
    edgeType = selectedEdges[0].objectType

    # get selected sketch line, and other objects
    if edgeType == 'adsk::fusion::SketchLine':
        sketchLine = adsk.fusion.SketchLine.cast(selectedEdges[0])
    elif edgeType == 'adsk::fusion::SketchArc':
        sketchLine = adsk.fusion.SketchArc.cast(selectedEdges[0])
    else:
        # write error message
        ui.MessageBox('Please select a line or arc.')
        return

    sketch = sketchLine.parentSketch
    sketchPlane = sketch.referencePlane
    sketchNormal  = sketchPlane.geometry.normal
    extrudes = rootComp.features.extrudeFeatures
    points = sketch.sketchPoints
    lines = sketch.sketchCurves.sketchLines
    
    # calc the number of points to create
    numberOfPoints = int(((maxNumber - minNumber) / steps) + 1)
    
    #calculate and create the points for the numbers
    
    evaluator = sketchLine.geometry.evaluator
    testBool, testStart, testEnd = evaluator.getParameterExtents()
    
    for i in range(numberOfPoints):
        # get the current point
        currentIteration = i / (numberOfPoints - 1)
        currentPosition = testEnd * currentIteration
        testBool2, point = evaluator.getPointAtParameter(currentPosition)
        # get the text vector with rotation matrix
        rotationMatrix = adsk.core.Matrix3D.create()
        result = rotationMatrix.setToRotation(angle, sketchNormal, point)
        result, textVector = evaluator.getTangent(currentPosition)
        result = textVector.transformBy(rotationMatrix)
        # calculate second point for sketch line
        vectorOnCurve = point.asVector()
        
        currentLine = createLine(lines, vectorOnCurve, textVector, alignment)
        
        numberStr = createTextString(i, steps, minNumber, prefix, postfix)
        
        createTextOnLine(sketch, currentLine, textVector, numberStr, numberHeight, alignment, onPath)
        
    sketchProfiles = adsk.core.ObjectCollection.create()
    
    for textItem in sketch.sketchTexts:
        sketchProfiles.add(textItem)
    
    extrusionDistance = adsk.core.ValueInput.createByReal(distance)
    setDistance = adsk.fusion.DistanceExtentDefinition.create(extrusionDistance)

    extrudeInput = extrudes.createInput(sketchProfiles, operationValues[operation])
    extrudeInput.setOneSideExtent(setDistance, adsk.fusion.ExtentDirections.PositiveExtentDirection)
    # Get the extrusion body
    extrude1 = extrudes.add(extrudeInput)
    numbersBody = extrude1.bodies.item(0)
    numbersBody.name = "consNumbers"
    
    return 

    # define the start and end points of the operation
    startVector = sketchLine.startSketchPoint.geometry.asVector()
    endVector = sketchLine.endSketchPoint.geometry.asVector()
    lineVector = endVector.copy()
    lineVector.subtract(startVector)

    # calulate vector for text path

    # Keep angle between 0 and 360° and keep text on same side of line
    angleRad = angle % (math.pi*2)
    if angleRad < 0:
        angleRad += math.p*2
    textFlip = False
    isAbovePath = False
    if angleRad > math.pi/2 and angleRad <= (1.5*math.pi):
        isAbovePath = True
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
        if alignmentValues[alignment] == alignmentValues["Left"] or alignmentValues[alignment] == alignmentValues["Center"]:
            currentStartVector.add(pathVector)
        currentEndVector = currentPointVector.copy()
        if alignmentValues[alignment] == alignmentValues["Right"] or alignmentValues[alignment] == alignmentValues["Center"]:
            currentEndVector.subtract(pathVector)
        textLine = lines.addByTwoPoints(currentStartVector.asPoint(), currentEndVector.asPoint())

        # Build text with pre- and postfix
        numberStr = str(iteration * steps + minNumber)
        if prefix != "":
            if prefix[-1] != " ":
                prefix = prefix + " "
        if postfix != "":
            if postfix[0] != " ":
                postfix = " " + postfix
        numberStr = prefix + numberStr + postfix

        textInput = skTexts.createInput2(numberStr, numberHeight)
        textInput.setAsAlongPath(textLine, isAbovePath, alignmentValues[alignment], 0)
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

    extrudeInput = extrudes.createInput(sketchProfiles, operationValues[operation])
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
    
# reverse order of min and max number
def reverseOrder(minNumber, maxNumber):
    temp = minNumber
    minNumber = maxNumber
    maxNumber = temp
    return minNumber, maxNumber

# create new line dpending on text alignment
def createLine(sketchLines, vectorOnCurve, textVecor, textAlignment):
    # calculate start and end vecotors
    startVector = vectorOnCurve.copy()
    endVector = vectorOnCurve.copy()
    if alignmentValues[textAlignment] == alignmentValues["Left"] or alignmentValues[textAlignment] == alignmentValues["Center"]:
        result = endVector.add(textVecor)
    if alignmentValues[textAlignment] == alignmentValues["Right"] or alignmentValues[textAlignment] == alignmentValues["Center"]:
        result = startVector.subtract(textVecor)
    
    startPoint = startVector.asPoint()
    endPoint = endVector.asPoint()
    
    newLine = sketchLines.addByTwoPoints(startPoint, endPoint)
    
    return newLine

def createTextString(iteration, steps, minNumber, prefix, postfix):
    numberStr = str(iteration * steps + minNumber)
    if prefix != "":
        if prefix[-1] != " ":
            prefix = prefix + " "
    if postfix != "":
        if postfix[0] != " ":
            postfix = " " + postfix
    numberStr = prefix + numberStr + postfix
    return numberStr

def createTextOnLine(sketch, line, textVector, text, textHeight, alignment, onPath):
    sketchTexts = sketch.sketchTexts
    #get base vector for sketch
    baseVector = sketch.xDirection
    textInput = sketchTexts.createInput2(text, textHeight)
    #calculate angle between text vector and base vector
    angle = textVector.angleTo(baseVector)
    flip, newAlignment = calcTextFlip(angle, alignment)
    
    # calc if text is above or below line
    isAbovePath = onPathToBool(onPath)
    if flip == True:
        isAbovePath = not isAbovePath  
    
    textInput.setAsAlongPath(line, isAbovePath, alignmentValues[newAlignment], 0)
    textInput.isVerticalFlip = flip
    textInput.isHorizontalFlip = flip
    
    try:
        sketchTexts.add(textInput)
    except:
        textInput.fontName = 'Arial'
        sketchTexts.add(textInput)
        
# Keep angle between 0 and 360° and keep text on same side of line
def calcTextFlip(angle, alignment):
    angleRad = angle % (math.pi*2)
    if angleRad < 0:
        angleRad += math.p*2
    textFlip = False
    if angleRad > math.pi/2 and angleRad <= (1.5*math.pi):
        textFlip = True
    else:
        alignment = flipAlignment(alignment)
    return textFlip, alignment

#flip alignment of text
def flipAlignment(alignment):
    if alignment == "Left":
        return "Right"
    if alignment == "Right":
        return "Left"
    if alignment == "Center":
        return "Center"
    
def onPathToBool(onPath):
    if onPath == "On Top":
        return True
    else:
        return False