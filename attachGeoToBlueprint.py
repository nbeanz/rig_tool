import maya.cmds as cmds
from functools import partial
import System.utils as utils
reload(utils)

class AttachGeoToBlueprint_ShelfTool: #130 129
    def attachWithParenting(self):
        self.parenting=True
        self.skinning=True
        self.processInitialSelection()
        print("aaa1")

    def attachWithSkinning(self):
        self.skinning=True
        self.parenting=False
        self.processInitialSelection()
        print("aaa")

    def processInitialSelection(self):
        print self.skinning
        print self.parenting

        selection=cmds.ls(selection=True)
        self.blueprintJoints=[]
        self.geometry=[]

        self.blueprintJoints=self.findBlueprintJoints(selection)
        self.geometry=self.findGeometry(selection)

        print self.blueprintJoints

    def findBlueprintJoints(self, selection):
        selectedBlueprintJoints=[]
        for object in selection:
            if cmds.objectType(object, isType="joint"):
                jointNameInfo=utils.stripAllNamespaces(object)
                if jointNameInfo!=None:
                    jointName=jointNameInfo[1]
                    if jointName.find("blueprint_")==0:
                        selectedBlueprintJoints.append(object)
        if len(selectedBlueprintJoints)>0:
            return selectedBlueprintJoints
        else:
            return None
