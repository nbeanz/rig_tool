import maya.cmds as cmds

def findAllModules(relativeDirectory):
    #search modules directory for all available Modules
    #return a list of all module names
    allPyFiles=findAllFiles(relativeDirectory,".py")
    returnModules=[]
    for file in allPyFiles:
        if file!="__init__":
            returnModules.append(file)
    return returnModules

def findAllModuleNames(relativeDirectory):
    validModules=findAllModules(relativeDirectory)
    validModuleNames=[]

    packageFolder=relativeDirectory.partition("/Modules/")[2]

    for m in validModules:
        mod=__import__(packageFolder+"."+m,{}, {}, [m])
        reload(mod)

        validModuleNames.append(mod.CLASS_NAME)
    return(validModules, validModuleNames)

def findAllMayaFiles(relativeDirectory):
    return findAllFiles(relativeDirectory, ".ma")

def findAllFiles(relativeDirectory, fileExtension):
    #searcb th erealtive directory for all files with given fileExtension

    import os
    fileDirectory=os.environ['RIGGING_TOOL_ROOT']+"/"+relativeDirectory+"/"
    #print fileDirectory

    allFiles=os.listdir(fileDirectory)
    #refine all files listing only those of the specified file ext
    returnFiles=[]
    for f in allFiles:
        splitString = str(f).rpartition(fileExtension)
        if not splitString[1]== "" and splitString[2]=="":
            returnFiles.append(splitString[0])

    return returnFiles

def findHighestTrailingNumber(names, basename):
    import re
    highestValue=0
    for n in names:
        if n.find(basename)==0:
            suffix=n.partition(basename)[2]
            if re.match("^[0-9]*$",suffix):
                numericalElement=int(suffix)
                if numericalElement>highestValue:
                    highestValue=numericalElement
    return highestValue

def stripLeadingNamespace(nodeName):
    if nodeName.find(":")== -1:
        return None
    splitString=str(nodeName).partition(":")
    return [splitString[0], splitString[2]]

def stripAllNamespaces(nodeName):
    if str(nodeName).find(":")==-1:
        return None
    splitString=str(nodeName).rpartition(":")
    return [splitString[0], splitString[2]]

def basic_stretchy_IK(rootJoint, endJoint, container=None, lockMinimumLength=True, poleVectorObject=None, scaleCorrectionAttribute=None):
    from math import fabs
    containedNodes=[]

    totalOriginalLength=0.0
    done=False
    parent=rootJoint
    childJoints=[]
    while not done:
        children=cmds.listRelatives(parent, children=True)
        children=cmds.ls(children, type="joint")

        if len(children)==0:
            done=True
        else:
            child=children[0]
            childJoints.append(child)
            totalOriginalLength+=fabs(cmds.getAttr(child+".translateX"))
            parent=child
            if child==endJoint:
                done=True

    ikNodes=cmds.ikHandle(sj=rootJoint, ee=endJoint, sol="ikRPsolver", n=rootJoint+"_ikHandle")
    ikNodes[1]=cmds.rename(ikNodes[1], rootJoint+"_ikEffector")
    ikEffector=ikNodes[1]
    ikHandle=ikNodes[0]

    cmds.setAttr(ikHandle+".visibility",0)
    containedNodes.extend(ikNodes)

    if poleVectorObject == None:
        poleVectorObject=cmds.spaceLocator(n=ikHandle+"_poleVectorLocator")[0]
        containedNodes.append(poleVectorObject)
        cmds.xform(poleVectorObject, worldSpace=True, absolute=True, translation=cmds. xform(rootJoint,q=True,worldSpace=True, translation=True))
        cmds.xform(poleVectorObject, worldSpace=True, relative=True, translation=[0.0, 1.0, 0.0])
        cmds.setAttr(poleVectorObject+".visibility",0)

    poleVectorConstraint=cmds.poleVectorConstraint(poleVectorObject, ikHandle)[0]
    containedNodes.append(poleVectorConstraint)
    #create root and end locator
    rootLocator=cmds.spaceLocator(n=rootJoint+"_rootPosLocator")[0]
    rootLocator_pointConstraint=cmds.pointConstraint(rootJoint, rootLocator, maintainOffset=False, n=rootLocator+"_pointConstraint")[0]
    endLocator=cmds.spaceLocator(n=endJoint+"_endPosLocator")[0]
    cmds.xform(endLocator,worldSpace=True, absolute=True, translation=cmds.xform(ikHandle, q=True, worldSpace=True, translation=True))
    ikHandle_pointConstraint=cmds.pointConstraint(endLocator, ikHandle,maintainOffset=False, n=ikHandle+"_pointConstraint")[0]
    containedNodes.extend([rootLocator, endLocator, rootLocator_pointConstraint, ikHandle_pointConstraint])

    cmds.setAttr(rootLocator+".visibility",0)
    cmds.setAttr(endLocator+".visibility",0)

    #grab distance between locators ###
    rootLocatorWithoutNamespace=stripAllNamespaces(rootLocator)[1]
    endLocatorWithoutNamespace=stripAllNamespaces(endLocator)[1]
    moduleNamespace=stripAllNamespaces(rootJoint)[0]
    distNode=cmds.shadingNode("distanceBetween",asUtility=True, n=moduleNamespace+":distBetween_"+rootLocatorWithoutNamespace+"_"+endLocatorWithoutNamespace)
    containedNodes.append(distNode)

    cmds.connectAttr(rootLocator+"Shape.worldPosition[0]",distNode+".point1")
    cmds.connectAttr(endLocator+"Shape.worldPosition[0]", distNode+".point2")
    scaleAttr=distNode+".distance"

    #divide disrance by total orginal length-scale factor
    scaleFactor=cmds.shadingNode("multiplyDivide", asUtility=True, n=ikHandle+"._scaleFactor")
    containedNodes.append(scaleFactor)
    cmds.setAttr(scaleFactor+".operation",2)
    cmds.connectAttr(scaleAttr,scaleFactor+".input1X")
    cmds.setAttr(scaleFactor+".input2X",totalOriginalLength)

    translationDriver=scaleFactor+".outputX"
    for joint in childJoints:
        multNode=cmds.shadingNode("multiplyDivide", asUtility=True, n=joint+"_scaleMultiply")
        containedNodes.append(multNode)
        cmds.setAttr(multNode+".input1X", cmds.getAttr(joint+".translateX"))
        cmds.connectAttr(translationDriver, multNode+".input2X")
        cmds.connectAttr(multNode+".outputX", joint+".translateX")
            #25 vid
    if container !=None:
        #cmds.container(container, edit=True, addNode=containedNodes, ihb=True) vid23
        addNodeToContainer(container, containedNodes,ihb=True)

    returnDict={}
    returnDict["ikHandle"]=ikHandle
    returnDict["ikEffector"]=ikEffector
    returnDict["rootLocator"]=rootLocator
    returnDict["endLocator"]=endLocator
    returnDict["poleVectorObject"]=poleVectorObject
    returnDict["ikHandle_pointConstraint"]=ikHandle_pointConstraint
    returnDict["rootLocator_pointConstraint"]=rootLocator_pointConstraint

    return returnDict

def forceSceneUpdate():
    cmds.setToolTo("moveSuperContext")
    nodes=cmds.ls()

    for n in nodes:
        cmds.select(n, replace=True)
    cmds.select(clear=True)
    cmds.setToolTo("selectSuperContext")

def addNodeToContainer(container, nodesIn, ihb=False, includeShapes=False, force=False):
    import types

    nodes=[]
    if type(nodesIn) is types.ListType:
        nodes=list(nodesIn)
    else:
        nodes=[nodesIn]

    convertionNodes=[]
    for node in nodes:
        node_conversionNodes=cmds.listConnections(node, source=True, destination=True)
        node_conversionNodes=cmds.ls(node_conversionNodes, type="unitConversion")

        convertionNodes.extend(node_conversionNodes)

    nodes.extend(convertionNodes)
    cmds.container(container, edit=True, addNode=nodes, ihb=ihb, includeShapes=includeShapes, force=force)

def doesBlueprintUserSpecifiedNameExist(name):
    cmds.namespace(setNamespace=":")
    namespaces=cmds.namespaceInfo(listOnlyNamespaces=True)

    names=[]
    for namespace in namespaces:
        if namespace.find("__")!=-1:
            names.append(namespace.partition("__")[2])
    return name in names

def RP_2segment_stretchy_IK(rootJoint, hingeJoint, endJoint, container=None, scaleCorrenctionAttribute=None):
    moduleNamespaceInfo=stripAllNamespaces(rootJoint)  #106
    moduleNamespace=""
    if moduleNamespaceInfo!=None:
        moduleNamespace=moduleNamespaceInfo[0]

    rootLocation=cmds.xform(rootJoint, q=True, worldSpace=True, translation=True)
    elbowLocation=cmds.xform(hingeJoint, q=True, worldSpace=True, translation=True)
    endLocation=cmds.xform(endJoint, q=True, worldSpace=True, translation=True)

    ikNodes=cmds.ikHandle(sj=rootJoint, ee=endJoint, n=rootJoint+"_ikHandle", solver="ikRPsolver")
    ikNodes[1]=cmds.rename(ikNodes[1], rootJoint+"_IKEffector")
    ikEffector=ikNodes[1]
    ikHandle=ikNodes[0]

    cmds.setAttr(ikHandle+".visibility",0)

    rootLoc=cmds.spaceLocator(n=rootJoint+"_positionLocator")[0]
    cmds.xform(rootLoc, worldSpace=True, absolute=True, translation=rootLocation)
    cmds.parent(rootJoint, rootLoc, absolute=True)

    endLoc=cmds.spaceLocator(n=ikHandle+"_positionLocator")[0]
    cmds.xform(endLoc, worldSpace=True, absolute=True, translation=endLocation)
    cmds.parent(ikHandle, endLoc, absolute=True)

    elbowLoc=cmds.spaceLocator(n=hingeJoint+"_positionLocator")[0]
    cmds.xform(elbowLoc, worldSpace=True, absolute=True, translation=elbowLocation)
    elbowLocConstraint=cmds.poleVectorConstraint(elbowLoc, ikHandle)[0]

    utilityNodes=[]
    for locators in ((rootLoc, elbowLoc, hingeJoint), (elbowLoc, endLoc, endJoint)):
        from math import fabs

        startLocNamespaceInfo=stripAllNamespaces(locators[0])
        startLocWithoutNamespace=""
        if startLocNamespaceInfo!=None:
            startLocWithoutNamespace=startLocNamespaceInfo[1]

        endLocNamespaceInfo=stripAllNamespaces(locators[1])
        endLocWithoutNamespace=""
        if endLocNamespaceInfo!=None:
            endLocWithoutNamespace=endLocNamespaceInfo[1]

        startLocShape=locators[0]+"Shape"
        endLocShape=locators[1]+"Shape"

        distNode=cmds.shadingNode("distanceBetween", asUtility=True, name=moduleNamespace+":distBetween_"+startLocWithoutNamespace+"_"+endLocWithoutNamespace)
        cmds.connectAttr(startLocShape+".worldPosition[0]", distNode+".point1")
        cmds.connectAttr(endLocShape+".worldPosition[0]", distNode+".point2")
        utilityNodes.append(distNode)

        scaleFactor=cmds.shadingNode("multiplyDivide", asUtility=True, n=distNode+"_scaleFactor")
        utilityNodes.append(scaleFactor)
        cmds.setAttr(scaleFactor+".operation",2)
        originalLength=cmds.getAttr(locators[2]+".translateX")
        cmds.connectAttr(distNode+".distance", scaleFactor+".input1X")
        cmds.setAttr(scaleFactor+".input2X", originalLength)
        translationDriver=scaleFactor+".outputX"

        translateX=cmds.shadingNode("multiplyDivide",asUtility=True, n=distNode+"_translationValue")
        utilityNodes.append(translateX)
        cmds.setAttr(translateX+".input1X", fabs(originalLength))
        cmds.connectAttr(translationDriver, translateX+".input2X")

        cmds.connectAttr(translateX+".outputX", locators[2]+".translateX")

    if container!=None:
        containedNodes=list(utilityNodes)
        containedNodes.extend(ikNodes)
        containedNodes.extend( [rootLoc, elbowLoc, endLoc] ) #[]
        containedNodes.append(elbowLocConstraint)

        addNodeToContainer(container, containedNodes, ihb=True)

    return (rootLoc, elbowLoc, endLoc, utilityNodes) #106


def findJointChain(rootJoint): #111
    joints=[rootJoint]
    parent=rootJoint
    done=False
    while not done:
        children=cmds.listRelatives(parent, children=True)
        children=cmds.ls(children, type="joint")

        if len(children)==0:
            done=True
        else:
            child=children[0]
            joints.append(child)
            parent=child

    return joints
