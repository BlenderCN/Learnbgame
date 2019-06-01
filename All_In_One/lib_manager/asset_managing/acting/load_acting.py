from PyQt5.QtWidgets import QSlider,QHBoxLayout
from PyQt5.QtCore import Qt
#from PyQt5.QtGui import QIcon,QKeySequence,QPixmap

import os
import bpy
from ...functions import clear_layout
from ...widgets import CheckBox

from . functions import  read_anim,find_fcurve_path

# Apply the pose or anim to the rig
def refresh_pose(self,action) :
    ob = bpy.context.scene.objects.active
    if ob.type=='ARMATURE' and ob.mode == 'POSE' :
        read_anim(self.action,self.blend.value()*0.01,self.action_left.isChecked(),self.action_right.isChecked(),self.selected_only.isChecked(),self.mirror_pose.isChecked(),self.frame_current)


def load_acting(self,ThumbnailList,item_info,link=True) :

    ob = bpy.context.scene.objects.active

    clear_layout(self.toolBoxLayout)

    self.frame_current = bpy.context.scene.frame_current

    self.blend = QSlider()
    self.blend.setOrientation(Qt.Horizontal)
    self.blend.setValue(100)
    self.blend.setMaximum(100)

    self.action_left = CheckBox('Left')
    self.action_left.setChecked(True)

    self.action_right = CheckBox('Right')
    self.action_right.setChecked(True)

    self.selected_only = CheckBox('Selected only')
    self.selected_only.setChecked(True)

    self.mirror_pose = CheckBox('Mirror')
    self.mirror_pose.setChecked(False)

    self.toolBoxLayout.addWidget(self.blend)

    row_L_R = QHBoxLayout()
    row_L_R.addWidget(self.action_right)
    row_L_R.addWidget(self.action_left)

    self.toolBoxLayout.addLayout(row_L_R)

    self.toolBoxLayout.addWidget(self.selected_only)
    self.toolBoxLayout.addWidget(self.mirror_pose)

    self.action = {}
    #item_basename = os.path.splitext(item.full_path)[0]
    action_txt = item_info['path']
    self.blend.setValue(100)

    with open(action_txt) as poseLib:
        for line in poseLib:
            fcurve = line.split("=")[0]
            value = eval(line.split("=")[1].replace("\n",""))

            self.action[fcurve] = value

    if ob :
        for fcurve,value in self.action.items():
            for path,channel in value.items() :

                #print(channel.items())
                for array_index,attributes in channel.items() :
                    correct_path = find_fcurve_path(ob,fcurve,path, array_index)
                    dstChannel = correct_path[0]

                    for index,keypose in enumerate(self.action[fcurve][path][array_index]) :
                        #print(keypose)
                        self.action[fcurve][path][array_index][index][1].append(dstChannel)
                        #if find_mirror(fcurve) :

    self.blend.valueChanged.connect(lambda : refresh_pose(self,action_txt))
    self.action_left.stateChanged.connect(lambda :refresh_pose(self,action_txt))
    self.action_right.stateChanged.connect(lambda :refresh_pose(self,action_txt))
    self.selected_only.stateChanged.connect(lambda : refresh_pose(self,action_txt))
    self.mirror_pose.stateChanged.connect(lambda : refresh_pose(self,action_txt))

    refresh_pose(self,action_txt)
