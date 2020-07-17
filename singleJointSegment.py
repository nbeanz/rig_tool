import maya.cmds as cmds
import os
import System.blueprint as blueprintMod
import System.utils as utils
reload(blueprintMod)

CLASS_NAME="SingleJointSegment"
TITLE="Single Joint Segment"
DESCRIPTION="Creates 2 joints"
ICON=os.environ["RIGGING_TOOL_ROOT"]+"/Icons/aaa.png"

class SingleJointSegment(blueprintMod.Blueprint):
    def __init__(self, userSpecifiedName, hookObj):
        jointInfo=[["root_joint",[0.0, 0.0, 0.0]], ["end_joint", [4.0, 0.0, 0.0]]]
        blueprintMod.Blueprint.__init__(self, CLASS_NAME, userSpecifiedName, jointInfo, hookObj)

    def install_custom(self,joints):
        self.createOrientationControl(joints[0], joints[1])

    def lock_phase1(self):
        jointPositions=[]
        jointOrientationValues=[]
        jointRotationOrders=[]

        joints=self.getJoints()

        for joint in joints:
            jointPositions.append(cmds.xform(joint, q=True, worldSpace=True, translation=True))

        cleanParent=self.moduleNamespace+":joints_grp"
        orientationInfo=self.orientationControlledJoint_getOrientation(joints[0], cleanParent)
        cmds.delete(orientationInfo[1])
        jointOrientationValues.append(orientationInfo[0])
        jointOrientations=(jointOrientationValues,None)
        jointRotationOrders.append(cmds.getAttr(joints[0]+".rotateOrder"))
        jointPreferredAngles=None
        hookObject=self.findHookObjectForLock()
        rootTransform=False

        moduleInfo=(jointPositions, jointOrientations, jointRotationOrders, jointPreferredAngles, hookObject, rootTransform)
        return moduleInfo

    def UI_custom(self):
        joints=self.getJoints()
        self.createRotationOrderUIControl(joints[0])

    def mirror_custom(self, originalModule):
        jointName=self.jointInfo[0][0]
        originalJoint=originalModule+":"+jointName
        newJoint=self.moduleNamespace+":"+jointName

        originalOrientationControl=self.getOrientationControl(originalJoint)
        newOrientationControl=self.getOrientationControl(newJoint)

        cmds.setAttr(newOrientationControl+".rotateX", cmds.getAttr(originalOrientationControl+".rotateX"))
