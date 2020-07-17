import maya.cmds as cmds
import os
import System.blueprint as blueprintMod
import System.utils as utils
reload(utils)
import Blueprint.singleOrientableJoint as singleOrientableJoint
reload(singleOrientableJoint)
#reload(blueprintMod)

CLASS_NAME="RootTransform"
TITLE="RootTransform"
DESCRIPTION="Creates a single joint with control for position and orientation"
ICON=os.environ["RIGGING_TOOL_ROOT"]+"/Icons/eee.png"

class RootTransform(singleOrientableJoint.SingleOrientableJoint): #101
    def __init__(self, userSpecifiedName, hookObject):
        print("derived class constr")
        jointInfo=[ ["joint",[0.0, 0.0, 0.0]] ]
        #blueprintMod.Blueprint.__init__(self, CLASS_NAME, userSpecifiedName, jointInfo, hookObject)
        super(singleOrientableJoint.SingleOrientableJoint,self).__init__( CLASS_NAME, userSpecifiedName, jointInfo, hookObject)

    def lock_phase1(self):
        moduleInfo=list(singleOrientableJoint.SingleOrientableJoint.lock_phase1(self))
        moduleInfo[5]=True
        return moduleInfo

        #106
