import maya.cmds as cmds
import os
import System.blueprint as blueprintMod
import System.utils as utils
reload(utils)
#reload(blueprintMod)

CLASS_NAME="SingleOrientableJoint"
TITLE="SingleOrientableJoint"
DESCRIPTION="Creates a single joint with control for position and orientation"
ICON=os.environ["RIGGING_TOOL_ROOT"]+"/Icons/ddd.png"

class SingleOrientableJoint(blueprintMod.Blueprint): #101
    def __init__(self, userSpecifiedName, hookObject):
        print("derived class constr")
        jointInfo=[ ["joint",[0.0, 0.0, 0.0]] ]
        blueprintMod.Blueprint.__init__(self, CLASS_NAME, userSpecifiedName, jointInfo, hookObject)

    def install_custom(self, joints):
        self.createSingleJointOrientaionControlAtJoint(joints[0])

    def mirror_custom(self, originalModule):
        jointName=self.jointInfo[0][0]
        originalJoint=originalModule+":"+jointName
        newJoint=self.moduleNamespace+":"+jointName
        originalOrientationControl=self.getSingleJointOrientationControl(originalJoint)
        newOrientationControl=self.getSingleJointOrientationControl(newJoint)

        oldRotation=cmds.getAttr(originalOrientationControl+".rotate")[0]
        cmds.setAttr(newOrientationControl+".rotate", oldRotation[0], oldRotation[1], oldRotation[2], type="double3")

    def UI_custom(self):
        joints=self.getJoints()
        self.createRotationOrderUIControl(joints[0])

    def lock_phase1(self):
        jointPositions=[]
        jointOrientationValues=[]
        jointRotationOrders=[]

        joint=self.getJoints()[0]
        jointPositions.append(cmds.xform(joint, q=True, worldSpace=True, translation=True))

        jointOrientationValues.append(cmds.xform(self.getSingleJointOrientationControl(joint),q=True, worldSpace=True, rotation=True))
        jointOrientations=(jointOrientationValues,None)
        jointRotationOrders.append(cmds.getAttr(joint+".rotateOrder"))
        jointPreferredAngles=None
        hookObject=self.findHookObjectForLock()
        rootTransform=False

        moduleInfo=(jointPositions, jointOrientations, jointRotationOrders, jointPreferredAngles, hookObject, rootTransform)
        return moduleInfo
