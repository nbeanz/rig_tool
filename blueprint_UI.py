'''blueprint_UI.py'''
import maya.cmds as cmds
import os
from functools import partial
import System.utils as utils
import importlib
reload(utils)

class Blueprint_UI:
    def __init__(self):
        #dictionary list of the UI elements.
        self.moduleInstance=None
        self.deleteSymmetryMoveExpressions()
        self.UIElements={}

        if cmds.window("blueprint_UI_window", exists=True):
            cmds.deleteUI("blueprint_UI_window")
        #init window
        windowWidth=200
        windowHeight=500
        tabHeight=windowHeight

        #window
        self.UIElements["window"]=cmds.window("blueprint_UI_window", width=windowWidth, height=windowHeight,title="blueprint window")
        self.UIElements["topLevelColumn"]=cmds.columnLayout(adjustableColumn=True, columnAlign="center")
        self.UIElements["tabs"]=cmds.tabLayout(height=tabHeight, width=tabHeight, innerMarginWidth=5, innerMarginHeight=5)

        tabWidth=cmds.tabLayout(self.UIElements["tabs"], q=True, width=True)
        self.scrollWidth=tabWidth-5

        #initualize module 1
        self.initialiseModuleTab(tabHeight,tabWidth)
        cmds.setParent(self.UIElements["tabs"])
        self.initialiseTemplatesTab(tabHeight, tabWidth)

        scenePublished=cmds.objExists("Scene_Published")
        sceneUnlocked=not cmds.objExists("Scene_Locked") and not scenePublished

        cmds.tabLayout(self.UIElements["tabs"], edit=1,tabLabelIndex=([1,"Modules"], [2, "Templates"]), enable=sceneUnlocked)
        cmds.setParent(self.UIElements["topLevelColumn"])
        self.UIElements["lockPublishColumn"]=cmds.columnLayout(adj=True, columnAlign="center", rs=3)
        cmds.separator()
        self.UIElements["lockBtn"]=cmds.button(label="Lock",c=self.lock, enable=sceneUnlocked)
        cmds.separator()
        self.UIElements["publishBtn"]=cmds.button(label="Publish", enable=not sceneUnlocked and not scenePublished)

        cmds.separator()

        cmds.showWindow(self.UIElements["window"])
        self.createScriptJob()

    def createScriptJob(self,*args):
        self.jobNum=cmds.scriptJob(event=["SelectionChanged", self.modifySelected], runOnce=True, parent=self.UIElements["window"])

    def deleteScriptJob(self):
        cmds.scriptJob(kill=self.jobNum)

    def initialiseModuleTab(self, tabHeight,tabWidth):

        moduleSpecific_scrollHeight=300
        scrollHeight=tabHeight-moduleSpecific_scrollHeight-50

        self.UIElements["moduleColumn"]=cmds.columnLayout(adj=1,rs=2)
        self.UIElements["moduleFrameLayout"]=cmds.frameLayout(height=scrollHeight, collapsable=False, borderVisible=False,labelVisible=False)
        self.UIElements["moduleList_Scroll"]=cmds.scrollLayout(hst=0)
        self.UIElements["moduleList_column"]=cmds.columnLayout(columnWidth=self.scrollWidth, adj=True, rs=2)

        cmds.separator()

        for module in utils.findAllModules("Modules/Blueprint"):
            self.createModuleInstallButton(module)
            cmds.setParent(self.UIElements["moduleList_column"])
            cmds.separator()
        cmds.setParent(self.UIElements["moduleColumn"])
        cmds.separator()


        self.UIElements["moduleName_row"]=cmds.rowLayout(nc=2, columnAttach=(1,"right",0), columnWidth=[(1,80)],adjustableColumn=2)
        cmds.text(label="Module Name:")
        self.UIElements["moduleName"]=cmds.textField(enable=False, alwaysInvokeEnterCommandOnReturn=True, enterCommand=self.renameModule)
        cmds.setParent(self.UIElements["moduleColumn"])

        columnWidth=tabWidth*0.32
        self.UIElements["moduleButtons_rowColumn"]=cmds.rowColumnLayout(numberOfColumns=3,ro=[(1,"both",2),(2,"both",2),(3,"both",2)],columnAttach=[(1,"both",3),(2,"both", 3),(3,"both",3)], columnWidth=[(1,columnWidth), (2,columnWidth),(3, columnWidth)])
        self.UIElements["rehookBtn"]=cmds.button(enable=False,label="Re-hook", c=self.rehookModule_setup)
        self.UIElements["snapRootBtn"]=cmds.button(enable=False, label="Snap,Root>Hook", c=self.snapRootToHook)
        self.UIElements["constrainRootBtn"]=cmds.button(enable=False, label="Constrain Root>Hook", c=self.constrainRootToHook)
        self.UIElements["groupSelectedBtn"]=cmds.button(label="Group Selected",c=self.groupSelected)
        self.UIElements["ungroupBtn"]=cmds.button(enable=False, label="Ungroup", c=self.ungroupSelected)
        self.UIElements["mirrorModuleBtn"]=cmds.button(enable=False, label="Mirror Module", c=self.mirrorSelection )
        self.UIElements["duplicateModuleBtn"]=cmds.button(enable=True, label="Duplicate", c=self.duplicateModule)
        self.UIElements["deleteModuleBtn"]=cmds.button(enable=False, label="Delete", c=self.deleteModule)
        self.UIElements["symmetryMoveCheckBox"]=cmds.checkBox(enable=True, label="Symmetry Move", onc=self.setupSymmetryMoveExpressions_CheckBox, ofc=self.deleteSymmetryMoveExpressions)
        cmds.setParent(self.UIElements["moduleColumn"])
        cmds.separator()

        #self.UIElements["moduleSpecificRowColumnLayout"]=cmds.rowColumnLayout(numberOfColumns=1)
        #self.UIElements["scrollLayout_spec"]=cmds.scrollLayout(hst=0)
        self.UIElements["moduleSpecific_column"]=cmds.columnLayout(columnWidth=250)
        cmds.setParent(self.UIElements["moduleColumn"])
        #cmds.separator()

    def createModuleInstallButton(self, module):
        mod =__import__("Blueprint."+module, (),(),[module])
        reload(mod)
        title=mod.TITLE
        description=mod.DESCRIPTION
        icon=mod.ICON

        buttonSize=60
        row=cmds.rowLayout(numberOfColumns=2, columnWidth=([1,buttonSize]), adjustableColumn=2,columnAttach=([1,"both",5],[2,"both",5]))
        self.UIElements["module_button"+module]=cmds.symbolButton(width=buttonSize, height=buttonSize, image=icon, command=partial(self.installModule,module))
        textColumn=cmds.columnLayout(columnAlign="center")
        cmds.text(align="center",width=buttonSize+325, label=title)
        cmds.scrollField(text=description,editable=False, width=buttonSize+325, height=buttonSize, wordWrap=True)
        cmds.setParent(self.UIElements["moduleList_column"])


    def installModule(self, module, *args):

        basename="instance_"
        cmds.namespace(setNamespace=":")
        namespaces=cmds.namespaceInfo(listOnlyNamespaces=True)

        for i in range(len(namespaces)):
            if namespaces[i].find("__")!=-1:
                namespaces[i]=namespaces[i].partition("__")[2]
        newSuffix=utils.findHighestTrailingNumber(namespaces,basename) +1
        userSpecName=basename+str(newSuffix)

        hookObj=self.findHookObjectFromSelection()

        mod=__import__("Blueprint."+module, (),(),[module])
        reload(mod)

        moduleClass=getattr(mod, mod.CLASS_NAME)
        moduleInstance=moduleClass(userSpecName, hookObj)
        moduleInstance.install()

        moduleTransform=mod.CLASS_NAME+"__"+userSpecName+":module_transform"
        cmds.select(moduleTransform,replace=True)
        cmds.setToolTo("moveSuperContext")
        ##27

    def isRootTransformInstalled(self):
        cmds.namespace(setNamespace=":")
        namespaces=cmds.namespaceInfo(listOnlyNamespaces=True)

        for namespace in namespaces:
            if namespace.find("RootTransform__")==0:
                return True
        return False

    def lock(self, *args): #128
        if not self.isRootTransformInstalled():
            result=cmds.confirmDialog(messageAlign="center", title="Lock Character", message="You have no rootTransform", button=["Yes", "No"], defaultButton="Yes", dismissString="Yes")
            if result == "Yes":
                pass  #128 idk

        result=cmds.confirmDialog(messageAlign="center", title="LockBlueprints",message="The action of the locking a character will convert the current blueprint modules to jnts \nThis action cannot be undone \nDo you want to continue?", button=["Accept", "Cancel"], defaultButton="Accept", cancelButton="Cancel", dismissString="Cancel")
        if result!="Accept":
            return

        self.deleteSymmetryMoveExpressions()
        cmds.checkBox(self.UIElements["symmetryMoveCheckBox"], edit=True, value=False)

        #self.deleteScriptJob() #86

        moduleInfo=[]
        cmds.namespace(setNamespace=":")
        namespaces=cmds.namespaceInfo(listOnlyNamespaces=True)

        moduleNameInfo=utils.findAllModuleNames("/Modules/Blueprint")
        validModules=moduleNameInfo[0]
        validModuleNames=moduleNameInfo[1]

        for n in namespaces:
            splitString=n.partition("__")
            if splitString[1]!="":
                module=splitString[0]
                userSpecifiedName=splitString[2]

                if module in validModuleNames:
                    index=validModuleNames.index(module)
                    moduleInfo.append([validModules[index],userSpecifiedName])

        if len(moduleInfo)==0:
            cmds.confirmDialog(messageAlign="center", title="LockBlueprints", message="no blueprint module instances", button=["Accept"],defaultButton="Accept")
            return

        moduleInstances=[]
        for module in moduleInfo:
            mod=__import__("Blueprint."+module[0],{}, {}, [module[0]])
            reload(mod)

            moduleClass=getattr(mod, mod.CLASS_NAME)
            moduleInst=moduleClass(module[1], None)
            moduleInfo=moduleInst.lock_phase1()
            moduleInstances.append((moduleInst, moduleInfo))

        for module in moduleInstances:
            module[0].lock_phase2(module[1])

        groupContainer="Group__container" #check __ or _ ne znam meni se?
        if cmds.objExists(groupContainer):
            cmds.lockNode(groupContainer, lock=False, lockUnpublished=False)
            cmds.delete(groupContainer)

        for module in moduleInstances:
            hookObject=module[1][4]
            module[0].lock_phase3(hookObject)

        sceneLockedLocator=cmds.spaceLocator(n="Scene_Locked")[0]
        cmds.setAttr(sceneLockedLocator+".visibility",0)
        cmds.lockNode(sceneLockedLocator, lock=True, lockUnpublished=True)
        cmds.select(clear=True)
        self.modifySelected()
        cmds.tabLayout(self.UIElements["tabs"], edit=True, enable=False)
        cmds.button(self.UIElements["lockBtn"], edit=True, enable=False)
        cmds.button(self.UIElements["publishBtn"], edit=True, enable=True)

    def modifySelected(self, *args):
        if cmds.checkBox(self.UIElements["symmetryMoveCheckBox"],q=True, value=True):
            self.deleteSymmetryMoveExpressions()
            self.setupSymmetryMoveExpressions()

        #print(" modify selected script job event")
        selectedNodes=cmds.ls(selection=True)

        if len(selectedNodes)<=1:
            self.moduleInstance=None
            selectedModuleNamespace=None
            currentModuleFile=None

            cmds.button(self.UIElements["ungroupBtn"], edit=True, enable=False)
            cmds.button(self.UIElements["mirrorModuleBtn"], edit=True, enable=False)

            if len(selectedNodes)==1:
                lastSelected=selectedNodes[0]
                if lastSelected.find("Group__")==0:
                    cmds.button(self.UIElements["ungroupBtn"], edit=True, enable=True)
                    cmds.button(self.UIElements["mirrorModuleBtn"], edit=True, enable=True, label="Mirror Group")
                namespaceAndNode=utils.stripLeadingNamespace(lastSelected)
                if namespaceAndNode!=None:
                    namespace=namespaceAndNode[0]
                    moduleNameInfo=utils.findAllModuleNames("/Modules/Blueprint")
                    validModules=moduleNameInfo[0]
                    validModuleNames=moduleNameInfo[1]

                    index=0
                    for moduleName in validModuleNames:
                        moduleNameIncSuffix=moduleName+"__"
                        if namespace.find(moduleNameIncSuffix)==0:
                            currentModuleFile=validModules[index]
                            selectedModuleNamespace=namespace
                            break
                        index+=1
            controlEnable=False
            constrainCommand=self.constrainRootToHook
            constrainLabel="Constrain root > Hook"

            userSpecifiedName=""
            if selectedModuleNamespace!=None:
                controlEnable=True
                userSpecifiedName=selectedModuleNamespace.partition("__")[2]

                mod=__import__("Blueprint."+currentModuleFile, {}, {}, [currentModuleFile])
                reload(mod)
                moduleClass=getattr(mod, mod.CLASS_NAME)
                print("moduleClass", moduleClass)

                print("currentModuleFile", currentModuleFile)
                print("selectedModuleNamespace", selectedModuleNamespace)
                print("userSpecifiedName", userSpecifiedName)

                self.moduleInstance=moduleClass(userSpecifiedName, None)
                print("self.moduleInstance ", self.moduleInstance)
                self.createModuleSpecificControls(userSpecifiedName)

                cmds.button(self.UIElements["mirrorModuleBtn"],edit=True, enable=True, label="Mirror Module")

                if self.moduleInstance.isRootConstrained():
                    constrainCommand=self.unconstrainRootFromHook
                    constrainLabel="Unconstrain Root"

            cmds.button(self.UIElements["rehookBtn"], edit=True, enable=controlEnable)
            cmds.button(self.UIElements["snapRootBtn"], edit=True, enable=controlEnable)
            cmds.button(self.UIElements["constrainRootBtn"], edit=True, enable=controlEnable, label= constrainLabel,c=constrainCommand)
            cmds.button(self.UIElements["deleteModuleBtn"], edit=True, enable=controlEnable,c=self.deleteModule)
            cmds.textField(self.UIElements["moduleName"], edit=True, enable=controlEnable, text=userSpecifiedName)
            self.createScriptJob()

    def createModuleSpecificControls(self, userSpecName):
        existingControls=cmds.columnLayout(self.UIElements["moduleSpecific_column"], q=True, childArray=True)
        if existingControls!=None:
            cmds.deleteUI(existingControls)
        cmds.setParent(self.UIElements["moduleSpecific_column"])

        if self.moduleInstance!=None:
            self.moduleInstance.UI(self, self.UIElements["moduleSpecific_column"])
            #print("aaaa", self.moduleInstance)

    def deleteModule(self, *args):
        symmetryMove=cmds.checkBox(self.UIElements["symmetryMoveCheckBox"],q=True, value=True)
        if symmetryMove:
            self.deleteSymmetryMoveExpressions()

        self.moduleInstance.delete()
        cmds.select(clear=True)

        if symmetryMove:
            self.setupSymmetryMoveExpressions_CheckBox() #93

    def renameModule(self, *args):
        newName=cmds.textField(self.UIElements["moduleName"], q=True, text=True)

        symmetryMove=cmds.checkBox(self.UIElements["symmetryMoveCheckBox"],q=True, value=True)
        if symmetryMove:
            self.deleteSymmetryMoveExpressions()

        self.moduleInstance.renameModuleInstance(newName)

        if symmetryMove:
            self.setupSymmetryMoveExpressions_CheckBox() #93

        previousSelection=cmds.ls(selection=True)
        if len(previousSelection)>0:
            cmds.select(previousSelection, replace=True)
        else:
            cmds.select(clear=True)

    def findHookObjectFromSelection(self, *args):
        selectedNodes=cmds.ls(selection=True, transforms=True)
        numberOfObjects=len(selectedNodes)
        hookObj=None
        if numberOfObjects!=0:
            hookObj=selectedNodes[numberOfObjects-1]
        return hookObj

    def rehookModule_setup(self, *args):
        selectedNodes=cmds.ls(selection=True, transforms=True)
        if len(selectedNodes)==2:
            print("two objects selected")
            newHook=self.findHookObjectFromSelection()
            self.moduleInstance.rehook(newHook)
            self.createScriptJob()
            ####stops the event loop remembers one isntance doesnt take the selected instances! mirror problem 2
        else:
            print("one obj selected")
            self.deleteScriptJob()
            currentSelection=cmds.ls(selection=True)
            cmds.headsUpMessage("Please select the joint you wish to rehook to.")
            cmds.scriptJob(event=["SelectionChanged", partial(self.rehookModule_callback, currentSelection)], runOnce=True)

    def rehookModule_callback(self, currentSelection):
        newHook=self.findHookObjectFromSelection()
        self.moduleInstance.rehook(newHook)
        if len(currentSelection)>0:
            cmds.select(currentSelection, replace=True)
        else:
            cmds.select(clear=True)
        self.createScriptJob()

    def snapRootToHook(self, *args):
        self.moduleInstance.snapRootToHook()
        self.createScriptJob()

    def constrainRootToHook(self, *args):
        self.moduleInstance.constrainRootToHook()
        cmds.button(self.UIElements["constrainRootBtn"], edit=True, label="unconstrain root", c=self.unconstrainRootFromHook)

    def unconstrainRootFromHook(self, *args):
        self.moduleInstance.unconstrainRootFromHook()
        cmds.button(self.UIElements["constrainRootBtn"], edit=True, label="constrain root", c=self.constrainRootToHook)

    def groupSelected(self, *args):
        import System.groupSelected as groupSelected
        reload(groupSelected)

        groupSelected.GroupSelected().showUI()
        self.createScriptJob()

    def ungroupSelected(self, *args):
        import System.groupSelected as groupSelected
        reload(groupSelected)

        groupSelected.ungroupSelected()
        self.createScriptJob()

    def mirrorSelection(self, *args):
        import System.mirrorModule as mirrorModule
        reload(mirrorModule)

        mirrorModule.MirrorModule()
        self.createScriptJob()

    def setupSymmetryMoveExpressions_CheckBox(self, *args):
        self.deleteScriptJob()
        self.setupSymmetryMoveExpressions()
        self.createScriptJob()

    def setupSymmetryMoveExpressions(self, *args):
        cmds.namespace(setNamespace=":")
        selection=cmds.ls(selection=True, transforms=True)
        expressionContainer=cmds.container(n="symmetryMove_container")

        if len(selection)==0:
            return

        linkedObjs=[]
        for obj in selection:
            if obj in linkedObjs:
                continue

            if obj.find("Group__")==0:
                if cmds.attributeQuery("mirrorLinks", n=obj, exists=True):
                    mirrorLinks=cmds.getAttr(obj+".mirrorLinks")
                    groupInfo=mirrorLinks.rpartition("__")
                    mirrorObj=groupInfo[0]
                    axis=groupInfo[2]
                    linkedObjs.append(mirrorObj)
                    self.setupSymmetryMoveForObject(obj, mirrorObj,axis, translation=True, orientation=True, globalScale=True)

            else: #92 orientation works partially, translations is great, scale doesnt work

                objNamespaceInfo=utils.stripLeadingNamespace(obj)
                if objNamespaceInfo!=None:
                    if cmds.attributeQuery("mirrorLinks", n=objNamespaceInfo[0]+":module_grp", exists=True):
                        mirrorLinks=cmds.getAttr(objNamespaceInfo[0]+":module_grp.mirrorLinks")
                        moduleInfo=mirrorLinks.rpartition("__")
                        module=moduleInfo[0]
                        axis=moduleInfo[2]
                        if objNamespaceInfo[1].find("translation_control")!=-1:
                            mirrorObj=module+":"+objNamespaceInfo[1]
                            linkedObjs.append(mirrorObj)
                            self.setupSymmetryMoveForObject(obj, mirrorObj, axis, translation=True, orientation=False, globalScale=False)
                        elif objNamespaceInfo[1].find("module_transform")==0:
                            mirrorObj=module+":module_transform"
                            linkedObjs.append(mirrorObj)
                            self.setupSymmetryMoveForObject(obj, mirrorObj, axis, translation=True, orientation=True, globalScale=True)
                        elif objNamespaceInfo[1].find("orientation_control")!=-1:
                            mirrorObj=module+":"+objNamespaceInfo[1]
                            linkedObjs.append(mirrorObj)

                            expressionString=mirrorObj+".rotateX = "+obj+".rotateX;\n"
                            expression=cmds.expression(n=mirrorObj+"_symmetryMoveExpression", string=expressionString)
                            utils.addNodeToContainer(expressionContainer, expression)
                        elif objNamespaceInfo[1].find("SingleJointOrientation_control")!=-1:
                            mirrorObj=module+":"+objNamespaceInfo[1]
                            linkedObjs.append(mirrorObj)
                            expressionString+=mirrorObj+".rotateX = " + obj + ".rotateX;\n"
                            expressionString+=mirrorObj+".rotateY = " + obj + ".rotateY;\n"
                            expressionString+=mirrorObj+".rotateZ = " + obj + ".rotateZ;\n"
                            expression=cmds.expression(n=mirrorObj+"_symmetryMoveExpression", string=expressionString)
                            utils.addNodeToContainer(expressionContainer, expression)

        cmds.lockNode(expressionContainer, lock=True)
        cmds.select(selection, replace=True)

    def setupSymmetryMoveForObject(self, obj, mirrorObj, axis, translation, orientation, globalScale):
        duplicateObject=cmds.duplicate(obj, parentOnly=True, inputConnections=True, name=obj+"_mirrorHelper")[0]
        emptyGroup=cmds.group(empty=True, name=obj+"mirror_scale_grp")
        cmds.parent(duplicateObject, emptyGroup, absolute=True)
        ##91
        scaleAttribute=".scale"+axis
        #print("scaleAttribute" ,scaleAttribute)
        cmds.setAttr(emptyGroup+scaleAttribute,-1)
        #print("emptyGroup+scaleAttribute", emptyGroup+scaleAttribute)

        expressionString="namespace -setNamespace \":\";\n"
        if translation:
            expressionString+="$worldSpacePos=`xform -q -ws -translation "+obj+"`;\n"
        if orientation:
            expressionString+="$worldSpaceOrient=`xform -q -ws -rotation "+obj+"`;\n"
        attrs=[]
        if translation:
            attrs.extend([".translateX", ".translateY", ".translateZ"])
        if orientation:
            attrs.extend([".rotateX",".rotateY",".rotateZ"])

        for attr in attrs:
            expressionString+=duplicateObject+attr+" = "+obj+attr+";\n"
        i=0
        for axis in ["X", "Y", "Z"]:
            if translation:
                expressionString+=duplicateObject+".translate"+axis+" = $worldSpacePos["+str(i)+"];\n"
            if orientation:
                expressionString+=duplicateObject+".rotate"+axis+" = $worldSpaceOrient["+str(i)+"];\n"
            i+=1
        if globalScale:
            expressionString+=duplicateObject+".globalScale="+obj+".globalScale;\n"
        expression=cmds.expression(n=duplicateObject+"_symmetryMoveExpression", string=expressionString)
        constraint=""
        if translation and orientation:
            constraint=cmds.parentConstraint(duplicateObject, mirrorObj, maintainOffset=False, n=mirrorObj+"_symmetryMoveConstraint")[0]
        elif translation:
            constraint=cmds.pointConstraint(duplicateObject, mirrorObj, maintainOffset=False, n=mirrorObj+"_symmetryMoveConstraint")[0]
            print("translation")
        elif orientation:
            constraint=cmds.orientConstraint(duplicateObject, mirrorObj, maintainOffset=False, n=mirrorObj+"_symmetryMoveConstraint")[0]
            print("orientation4")
        if globalScale:
            cmds.connectAttr(duplicateObject+".globalScale", mirrorObj+".globalScale")
        utils.addNodeToContainer("symmetryMove_container", [duplicateObject,emptyGroup, expression, constraint], ihb=True )

    def deleteSymmetryMoveExpressions(self, *args):
        container="symmetryMove_container"
        if cmds.objExists(container):
            cmds.lockNode(container, lock=False)

            nodes=cmds.container(container,q=True, nodeList=True)
            nodes=cmds.ls(nodes, type=["parentConstraint", "pointConstraint", "orientConstraint"])

            if len(nodes)>0:
                cmds.delete(nodes)

            cmds.delete(container)

    def initialiseTemplatesTab(self, tabHeight, tabWidth):  #117
        self.UIElements["templatesColumn"]=cmds.columnLayout(adj=True, rs=3, columnAttach=["both", 0])
        self.UIElements["templatesFrameLayout"]=cmds.frameLayout(height=(tabHeight-100), collapsable=False, borderVisible=False, labelVisible=False )
        self.UIElements["templateList_Scroll"]=cmds.scrollLayout(hst=0)
        self.UIElements["templatesList_Column"]=cmds.columnLayout(adj=True, rs=2)

        cmds.separator()
        for template in utils.findAllMayaFiles("/Templates"):
            cmds.setParent(self.UIElements["templatesList_Column"])
            templateAndPath=os.environ["RIGGING_TOOL_ROOT"]+"/Templates/"+template+".ma"
            self.createTemplateInstallButton(templateAndPath)

        cmds.setParent(self.UIElements["templatesColumn"])
        cmds.separator()
        self.UIElements["prepareTemplateBtn"]=cmds.button(label="Prepare for Template",c=self.prepareForTemplate)
        cmds.separator()
        self.UIElements["saveCurrentBtn"]=cmds.button(label="Save Current as Template", c=self.saveCurrentAsTemplate)
        cmds.separator()

    def prepareForTemplate(self, *args):
        cmds.select(all=True)
        rootLevelNodes=cmds.ls(selection=True, transforms=True)

        filteredNodes=[]
        for node in rootLevelNodes:
            if node.find("Group__")==0:
                filteredNodes.append(node)
            else:
                nodeNamespaceInfo=utils.stripAllNamespaces(node)
                if nodeNamespaceInfo!=None:
                    if nodeNamespaceInfo[1]=="module_transform":
                        filteredNodes.append(node)

        if len(filteredNodes)>0:
            cmds.select(filteredNodes, replace=True)
            self.groupSelected()

    def saveCurrentAsTemplate(self, *args):
        self.saveTemplateUIElements={}

        if cmds.window("saveTEmplate_UI_window", exists=True):
            cmds.deleteUI("saveTEmplate_UI_window")
        windowWidth=100
        windowHeight=152
        self.saveTemplateUIElements["window"]=cmds.window("saveTEmplate_UI_window", width=300, height=200, title="Save Current as Template", sizeable=True)

        self.saveTemplateUIElements["topLevelColumn"]=cmds.columnLayout(adj=True, columnAlign="center", rs=3)
        self.saveTemplateUIElements["templateName_rowColumn"]=cmds.rowColumnLayout(nc=2, columnAttach=(1, "right", 0), columnWidth=[(1,90), (2,200)])

        cmds.text(label="Template name:")
        self.saveTemplateUIElements["templateName"]=cmds.textField(text="([a-z],[A-Z],[0-9] and _only)")

        cmds.text(label="Title:")
        self.saveTemplateUIElements["templateTitle"]=cmds.textField(text="Title")

        cmds.text(label="Description:")
        self.saveTemplateUIElements["templateDescription"]=cmds.textField(text="Description")

        cmds.text(label="Icon:")
        self.saveTemplateUIElements["templateIcon"]=cmds.textField(text="[programRoot]/Icons/iii.png")

        cmds.setParent(self.saveTemplateUIElements["topLevelColumn"])
        cmds.separator()
        columnWidth=(windowWidth/2)-5
        self.saveTemplateUIElements["button_row"]=cmds.rowLayout(nc=2, columnWidth=[(1, 100), (2, 100)], cat=[(1, "both", 10),(2, "both", 10)], columnAlign=[(1, "center"), (2, "center")])
        cmds.button(label="Accept", c=self.saveCurrentAsTemplate_AcceptWindow)
        cmds.button(label="Cancel", c=self.saveCurrentAsTemplate_CancelWindow)

        cmds.showWindow(self.saveTemplateUIElements["window"])

    def saveCurrentAsTemplate_CancelWindow(self, *args):
        cmds.deleteUI(self.saveTemplateUIElements["window"])

    def saveCurrentAsTemplate_AcceptWindow(self, *args): #120
        templateName=cmds.textField(self.saveTemplateUIElements["templateName"], q=True, text=True)
        programRoot=os.environ["RIGGING_TOOL_ROOT"]
        templateFileName=programRoot+"/Templates/"+templateName+".ma"

        if os.path.exists(templateFileName):
            cmds.confirmDialog(title="Save Current as Template", message="template already exists", button=["Accept"], defaultButton="Accept")
            return

        if cmds.objExists("Group_container"):
            cmds.select("Group_container", replace=True)
        else:
            cmds.select(clear=True)

        cmds.namespace(setNamespace=":")
        namespaces=cmds.namespaceInfo(listOnlyNamespaces=True)

        for n in namespaces:
            if n.find("__")!=-1:
                cmds.select(n+":module_container", add=True)
        cmds.file(templateFileName, exportSelected=True, type="mayaAscii")
        cmds.select(clear=True)

        title=cmds.textField(self.saveTemplateUIElements["templateTitle"], q=True, text=True)
        description=cmds.textField(self.saveTemplateUIElements["templateDescription"], q=True, text=True)
        icon=cmds.textField(self.saveTemplateUIElements["templateIcon"], q=True, text=True)
        if icon.find("[programRoot]")!=-1:
            icon=programRoot+icon.partition("[programRoot]")[2]

        templateDescriptionFileName=programRoot+"/Templates/"+templateName+".txt"
        f=open(templateDescriptionFileName,"w")
        f.write(title+"\n")
        f.write(description+"\n")
        f.write(icon+"\n")
        f.close()

        cmds.setParent(self.UIElements["templatesList_Column"])
        self.createTemplateInstallButton(templateFileName)
        cmds.showWindow(self.UIElements["window"])

        cmds.deleteUI(self.saveTemplateUIElements["window"])

    def createTemplateInstallButton(self, templateAndPath): #121
        buttonSize=64
        templateDescriptionFile=templateAndPath.partition(".ma")[0]+".txt"
        #print("templateDescriptionFile", templateDescriptionFile) #.txt.txt wrong extensitons
        f=open(templateDescriptionFile, "r")
        title=f.readline()[0:-1]
        description=f.readline()[0:1]
        icon=f.readline()[0:-1]
        f.close()

        row=cmds.rowLayout(width=self.scrollWidth, nc=2, columnWidth=([1, buttonSize], [2, self.scrollWidth-buttonSize]), adj=2, columnAttach=([1,"both", 0], [2, "both", 5]))
        self.UIElements["template_button_"+templateAndPath]=cmds.symbolButton(width=buttonSize, height=buttonSize, image=icon, command=partial(self.installTemplate, templateAndPath))
        textColumn=cmds.columnLayout(columnAlign="center")
        cmds.text(align="center", width=buttonSize, wordWrap=True)
        cmds.scrollField(text=description, editable=False, width=buttonSize, height=buttonSize, wordWrap=True)
        cmds.setParent(self.UIElements["templatesList_Column"])
        cmds.separator()

    def installTemplate(self, templateAndPath, *args): #125
        cmds.file(templateAndPath, i=True, namespace="TEMPLATE_1")
        self.resolveNamespaceClashes("TEMPLATE_1")
        groupContainer="TEMPLATE_1:Group_container"
        if cmds.objExists(groupContainer):
            self.resolveGroupNameClashes("TEMPLATE_1")
            cmds.lockNode(groupContainer, lock=False, lockUnpublished=False)
            oldGroupContainer="Group_container"
            if cmds.objExists(oldGroupContainer):
                cmds.lockNode(oldGroupContainer, lock=False, lockUnpublished=False)

                nodeList=cmds.container(groupContainer, q=True, nodeList=True)
                utils.addNodeToContainer(oldGroupContainer, nodeList, force=True)
                cmds.delete(groupContainer)
            else:
                cmds.rename(groupContainer, oldGroupContainer)
            cmds.lockNode(oldGroupContainer, lock=True, lockUnpublished=True)
            cmds.namespace(setNamespace=":")
            cmds.namespace(moveNamespace=("TEMPLATE_1", ":"), force=True)
            cmds.namespace(removeNamespace="TEMPLATE_1")

    def resolveNamespaceClashes(self, tempNamespace):
        returnNames=[]
        cmds.namespace(setNamespace=tempNamespace)
        namespaces=cmds.namespaceInfo(listOnlyNamespaces=True)
        cmds.namespace(setNamespace=":")
        existingNamespaces=cmds.namespaceInfo(listOnlyNamespaces=True)

        for i in range(len(namespaces)):
            namespaces[i]=namespaces[i].partition(tempNamespace+":")[2]

        for name in namespaces:
            newName=str(name)
            oldName=tempNamespace+":"+name
            wasRenamed=False

            if name in existingNamespaces:
                highestSuffix=utils.findHighestTrailingNumber(existingNamespaces, name+"_")
                highestSuffix+=1

                newName=str(name)+"_"+str(highestSuffix)
            returnNames.append([oldName, newName])
        #res0lve mirror links
        self.renameNamespaces(returnNames)
        return returnNames

    def renameNamespaces(self, names): #122
        for name in names:
            oldName=name[0]
            newName=name[1]
            cmds.namespace(setNamespace=":")
            cmds.namespace(add=newName)
            cmds.namespace(moveNamespace=[oldName, newName])
            cmds.namespace(removeNamespace=oldName)

    def resolveNameChangeMirrorLinks(self, names, tempNamespace): #123 #124
        print("test")
        moduleNamespaces=False
        firstOldNode=names[0][0]
        if utils.stripLeadingNamespace(firstOldNode)[1].find("Group__")==-1:
            moduleNamespaces=True

        for n in names:
            oldNode=n[0]
            if moduleNamespaces:
                oldNode+=":module_grp"

            if cmds.attributeQuery("mirrorLinks", n=oldNode, exists=True):
                mirrorLinks=cmds.getAttr(oldNode+".mirrorLinks")
                mirrorLinkInfo=mirrorLink.rpartition("__")
                mirrorNode=mirrorLinkInfo[0]
                mirrorAxis=mirrorLinkInfo[2]

                found=False
                container=""
                if moduleNamespaces:
                    oldNodeNamespace=n[0]
                    container=oldNodeNamespace+":module_container"
                else:
                    container=tempNamespace+":Group_container"

                for nm in names:
                    oldLink=nm[0].partition(tempNamespace+":")[2]
                    if oldLink==mirrorNode:
                        newLink=nm[1]

                        if cmds.objExists(container):
                            cmds.lockNode(container, lock=False, lockUnpublished=False)

                        cmds.setAttr(oldName+".mirrorLinks", newLink+"__"+mirrorAxis, type="string")
                        if cmds.objExists(container):
                            cmds.lockNode(container, lock=True, lockUnpublished=True)
                        found=True
                        break

                if not found:
                    if cmds.objExists(container):
                        cmds.lockNode(container, lock=False, lockUnpublished=False)

                    cmds.deleteAttr(oldNode, at="mirrorLinks")

                    if cmds.objExists(container):
                        cmds.lockNode(container, lock=True, lockUnpublished=True)

    def resolveGroupNameClashes(self, tempNamespace): #125
        cmds.namespace(setNamespace=tempNamespace)
        dependencyNodes=cmds.namespaceInfo(listOnlyDependencyNodes=True)
        cmds.namespace(setNamespace=":")
        transforms=cmds.ls(dependencyNodes, transforms=True)

        groups=[]
        for node in transforms:
            if node.find(tempNamespace+":Group__")==0:
                groups.append(node)

        if len(groups)==0:
            return groups
        groupNames=[]
        for group in groups:
            groupName=group.partition(tempNamespace+":")[2]
            newGroupName=str(groupName)

            if cmds.objExists(newGroupName):
                existingGroups=cmds.ls("Group__", transforms=True)
                highestSuffix=utils.findHighestTrailingNumber(existingGroups, groupName+"_")
                newGroupName=str(groupName)+"_"+str(highestSuffix)
            groupNames.append([group, newGroupName])
        self.resolveNameChangeMirrorLinks(groupNames, tempNamespace)
        groupContainer=tempNamespace+":Group_container"
        if cmds.objExists(groupContainer):
            cmds.lockNode(groupContainer, lock=False, lockUnpublished=False)
        for name in groupNames:
            cmds.rename(name[0], name[1])
        if cmds.objExists(groupContainer):
            cmds.lockNode(groupContainer, lock=True, lockUnpublished=True)

        return groupNames

    def duplicateModule(self, *args): #126
        modules=set([])
        groups=set([])

        selection=cmds.ls(selection=True, transforms=True)
        if len(selection)==0:
            return

        for node in selection:
            selectionNamespaceInfo=utils.stripLeadingNamespace(node)
            if selectionNamespaceInfo!=None:
                if selectionNamespaceInfo[0].find("__")!=-1:
                    modules.add(selectionNamespaceInfo[0])
            else:
                if node.find("Group__")==0:
                    groups.add(node)

        for group in groups:
            moduleInfo=self.duplicateModule_processGroup(group)
            for module in moduleInfo:
                modules.add(module)
        if len(groups)>0:
            groupSelection=list(groups)
            cmds.select(groupSelection, replace=True, hi=True)
        else:
            cmds.select(clear=True)

        for module in modules:
            cmds.select(module+":module_container", add=True)

        if len(groups)>0:
            cmds.lockNode("Group__container", lock=False, lockUnpublished=False) # _ __
        elif len(modules)==0:
            return

        duplicateFileName=os.environ["RIGGING_TOOL_ROOT"]+"/__duplicationCache.ma"
        cmds.file(duplicateFileName, exportSelected=True, type="mayaAscii", force=True)
        if len(groups)>0:
            cmds.lockNode("Group__container", lock=True, lockUnpublished=True) # _ __

        self.installDuplicate(duplicateFileName, selection)
        cmds.setToolTo("moveSuperContext")


    def installDuplicate(self, duplciatePath, selection, *args): #127
        cmds.file(duplciatePath, i=True, namespace="TEMPLATE_1")
        moduleNames=self.resolveNamespaceClashes("TEMPLATE_1")
        groupNames=self.resolveGroupNameClashes("TEMPLATE_1")
        groups=[]
        for name in groupNames:
            groups.append(name[1])

        if len(groups)>0:
            sceneGroupContainer="Group__container"
            cmds.lockNode(sceneGroupContainer, lock=False, lockUnpublished=False)
            utils.addNodeToContainer(sceneGroupContainer, groups, includeShapes=True, force=True)
            for group in groups:
                groupNiceName=group.partition("__")[2]
                cmds.container(sceneGroupContainer, edit=True, publishAndBind=[group+".translate", groupNiceName+"_t"])
                cmds.container(sceneGroupContainer, edit=True, publishAndBind=[group+".rotate", groupNiceName+"_r"])
                cmds.container(sceneGroupContainer, edit=True, publishAndBind=[group+".globalScale", groupNiceName+"_globalScale"])

            cmds.lockNode(sceneGroupContainer, lock=True, lockUnpublished=True)
        cmds.namespace(setNamespace=":")
        cmds.namespace(moveNamespace=("TEMPLATE_1", ":"), force=True)
        cmds.namespace(removeNamespace="TEMPLATE_1")

        newSelection=[]
        for node in selection:
            found=False
            for group in groupNames:
                oldName=group[0].partition("TEMPLATE_1:")[2]
                newName=group[1]
                if node==oldName:
                    newSelection.append(newName)
                    found=True
                    break

            if not found:
                nodeNamespaceInfo=utils.stripLeadingNamespace(node)
                if nodeNamespaceInfo!=None:
                    nodeNamespace=nodeNamespaceInfo[0]
                    nodeName=nodeNamespaceInfo[1]
                    searchName="TEMPLATE_1:"+nodeNamespace
                    for module in moduleNames:
                        if module[0] == searchName:
                            newSelection.append(module[1]+":"+nodeName)
        if len(newSelection)>0:
            cmds.select(newSelection, replace=True)

    def duplicateModule_processGroup(self, group): #126
        returnModules=[]
        children=cmds.listRelatives(group, children=True, type="transform")

        for c in children:
            selectionNamespaceInfo=utils.stripLeadingNamespace(c)
            if selectionNamespaceInfo!=None:
                returnModules.append(selectionNamespaceInfo[0])
            else:
                if c.find("Group__")==0:
                    returnModules.extend(self.duplicateModule_processGroup(c))
        return returnModules
