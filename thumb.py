
import maya.cmds as cmds
import os
import System.blueprint as blueprintMod
import Blueprint.finger as finger
import System.utils as utils
reload(utils)
#reload(blueprintMod)

CLASS_NAME="Thumb"
TITLE="Thumb"
DESCRIPTION="Creates 4 joints"
ICON=os.environ["RIGGING_TOOL_ROOT"]+"/Icons/ccc.png"

class Thumb(finger.Finger): #100
    def __init__(self, userSpecifiedName, hookObject):
        jointInfo=[["root_joint",[0.0, 0.0, 0.0]], ["knuckle_1_joint", [4.0, 0.0, 0.0]], ["knuckle_2_joint", [8.0, 0.0, 0.0]], ["end_joint", [12.0, 0.0, 0.0]]]
        super(finger.Finger,self).__init__( CLASS_NAME, userSpecifiedName, jointInfo, hookObject)

        #blueprintMod.Blueprint.__init__(self, CLASS_NAME, userSpecifiedName, jointInfo, hookObject)
        # https://stackoverflow.com/questions/1713038/super-fails-with-error-typeerror-argument-1-must-be-type-not-classobj-when/18392639
