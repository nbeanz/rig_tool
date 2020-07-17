import maya.cmds as cmds
import os
import System.blueprint as blueprintMod
import System.utils as utils
reload(utils)
#reload(blueprintMod)
import Blueprint.hingeJoint as hingeJoint

CLASS_NAME="legFoot"
TITLE="Leg and Foot"
DESCRIPTION="Creates 5 joints, hip-knee-ankle(hinge joint setup), ball-toe"
ICON=os.environ["RIGGING_TOOL_ROOT"]+"/Icons/ggg.png"

class legFoot(hingeJoint.HingeJoint): #107
    def __init__(self, userSpecifiedName, hookObject):
        jointInfo=[["hip_joint",[0.0, 0.0, 0.0]], ["knee_joint", [4.0, 0.0, -1.0]], ["ankle_joint", [8.0, 0.0, 0.0]], ["ball_joint", [0.0, -9.0, 3.0]], ["toe_joint", [0.0, -9.0, 6.0]]]
        super(hingeJoint.HingeJoint,self).__init__( CLASS_NAME, userSpecifiedName, jointInfo, hookObject)

    def install_custom(self, joints):
        hingeJoint.HingeJoint.install_custom(self, joints)
        ankleOrientationControl=self.createOrientationControl(joints[2], joints[3])
        ballOrientationControl=self.createOrientationControl(joints[3], joints[4])

        cmds.setAttr(ankleOrientationControl+".rotateX", 180)
        cmds.setAttr(ballOrientationControl+".rotateX", -90)
        cmds.xform(self.getTranslationControl(joints[1]), worldSpace=True, absolute=True, translation=[0.0, -4.0, 1.0])
        cmds.xform(self.getTranslationControl(joints[2]), worldSpace=True, absolute=True, translation=[0.0, -8.0, 0.0])

        for i in range(len(joints)-1):
            joint=joints[i]
            rotateOrder=3 #xzy
            if i>=2:
                rotateOrder=0 #xyz
            cmds.setAttr(joint+".rotateOrder", rotateOrder)

    def mirror_custom(self, originalModule):
        for i in range(2, 4):
            jointName=self.jointInfo[i][0]
            originalJoint=originalModule+":"+jointName
            newJoint=self.moduleNamespace+":"+jointName

            originalOrientationControl=self.getOrientationControl(originalJoint)
            newOrientationControl=self.getOrientationControl(newJoint)
            cmds.setAttr(newOrientationControl+".rotateX", cmds.getAttr(originalOrientationControl+".rotateX"))

    def UI_custom(self):
        hingeJoint.HingeJoint.UI_custom(self)

        joints=self.getJoints()
        self.createRotationOrderUIControl(joints[2])
        self.createRotationOrderUIControl(joints[3])

    def lock_phase1(self): #109
        moduleInfo=hingeJoint.HingeJoint.lock_phase1(self)
        jointPositions=moduleInfo[0]
        jointOrientationValues=moduleInfo[1][0]
        jointRotationOrders=moduleInfo[2]

        joints=self.getJoints()
        for i in range(3, 5):
            joint=joints[i]
            jointPositions.append(cmds.xform(joint, q=True, worldSpace=True, translation=True))
            jointRotationOrders.append(cmds.getAttr(joint+".rotateOrder"))

        cmds.lockNode(self.containerName, lock=False, lockUnpublished=False)

        jointNameInfo=utils.stripAllNamespaces(joints[1])
        cleanParent=jointNameInfo[0]+":IK_"+jointNameInfo[1]
        deleteJoints=[]
        for i in range(2,4):
            orientationInfo=self.orientationControlledJoint_getOrientation(joints[i], cleanParent)
            jointOrientationValues.append(orientationInfo[0])
            cleanParent=orientationInfo[1]
            deleteJoints.append(cleanParent)
        cmds.delete(deleteJoints)
        cmds.lockNode(self.containerName, lock=True, lockUnpublished=True)

        return moduleInfo
