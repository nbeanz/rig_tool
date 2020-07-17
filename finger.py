
import maya.cmds as cmds
import os
import System.blueprint as blueprintMod
import System.utils as utils
reload(utils)
#reload(blueprintMod)

CLASS_NAME="Finger"
TITLE="Finger"
DESCRIPTION="Creates 5 joints"
ICON=os.environ["RIGGING_TOOL_ROOT"]+"/Icons/bbb.png"

class Finger(blueprintMod.Blueprint): #95
    def __init__(self, userSpecifiedName, hookObject):
        jointInfo=[["root_joint",[0.0, 0.0, 0.0]], ["knuckle_1_joint", [4.0, 0.0, 0.0]], ["knuckle_2_joint", [8.0, 0.0, 0.0]], ["knuckle_3_joint", [12.0, 0.0, 0.0]], ["end_joint", [16.0, 0.0, 0.0]]]
        blueprintMod.Blueprint.__init__(self, CLASS_NAME, userSpecifiedName, jointInfo, hookObject)

    def install_custom(self, joints):#96
        for i in range(len(joints)-1):
            cmds.setAttr(joints[i]+".rotateOrder",3)
            self.createOrientationControl(joints[i], joints[i+1])
            paControl=self.createPreferredAngleRepresentation(joints[i],self.getTranslationControl(joints[i]),childOfOrientationControl=True)
            cmds.setAttr(paControl+".axis",3)

        if not self.mirrored:
            cmds.setAttr(self.moduleNamespace+":module_transform.globalScale",0.75)

    def mirror_custom(self, originalModule):
        for i in range(len(self.jointInfo)-1):
            jointName=self.jointInfo[i][0]
            originalJoint=originalModule+":"+jointName
            newJoint=self.moduleNamespace+":"+jointName

            originalOrientationControl=self.getOrientationControl(originalJoint)
            newOrientationControl=self.getOrientationControl(newJoint)

            cmds.setAttr(newOrientationControl+".rotateX", cmds.getAttr(originalOrientationControl+".rotateX"))
            originalPreferredAngleControl=self.getPreferredAngleControl(originalJoint)
            newPreferredAngleControl=self.getPreferredAngleControl(newJoint)

            cmds.setAttr(newPreferredAngleControl+".axis", cmds.getAttr(originalPreferredAngleControl+".axis"))

    def UI_custom(self):
        joints=self.getJoints()
        joints.pop()

        for joint in joints:
            self.createRotationOrderUIControl(joint)

        for joint in joints:
            self.createPreferredAngleUIControl(self.getPreferredAngleControl(joint))

    def lock_phase1(self):
        jointPositions=[]
        jointOrientationValues=[]
        jointRotationOrders=[]
        jointPreferredAngles=[]

        joints=self.getJoints()

        index=0
        cleanParent=self.moduleNamespace+":joints_grp"
        deleteJoints=[]
        for joint in joints:
            jointPositions.append(cmds.xform(joint, q=True, worldSpace=True, translation=True))
            jointRotationOrders.append(cmds.getAttr(joint+".rotateOrder"))

            if index<len(joints)-1:
                orientationInfo=self.orientationControlledJoint_getOrientation(joint, cleanParent)
                jointOrientationValues.append(orientationInfo[0])
                cleanParent=orientationInfo[1]
                deleteJoints.append(cleanParent)

                jointPrefAngles=[0.0, 0.0, 0.0]
                axis=cmds.getAttr(self.getPreferredAngleControl(joint)+".axis")

                if axis==0:
                    jointPrefAngles[1]=50.0
                elif axis==1:
                    jointPrefAngles[1]=-50.0
                elif axis==2:
                    jointPrefAngles[2]=50.0
                elif axis==3:
                    jointPrefAngles[2]=-50.0

                jointPreferredAngles.append(jointPrefAngles)
            index+=1

        jointOrientations=(jointOrientationValues, None)
        cmds.delete(deleteJoints)
        hookObject=self.findHookObjectForLock()
        rootTransform=False

        moduleInfo=(jointPositions, jointOrientations, jointRotationOrders, jointPreferredAngles, hookObject, rootTransform)
        return moduleInfo
