from PyQt5.QtWidgets import QHBoxLayout,QVBoxLayout,QSpacerItem,QSizePolicy
#from PyQt5.QtCore
#from PyQt5.QtGui

from ...widgets import SpinBox,CheckBox,Label,LineEdit
from ...functions import read_json

from . functions import  read_anim,find_fcurve_path,store_anim,write_anim

import bpy,os,json

working_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
settings = read_json(os.path.join(working_dir,"settings.json"))

def store_acting_settings(self):
    # Frame Range
    self.frameRangeLayout = QHBoxLayout()

    self.frameRangeIn = SpinBox()
    self.frameRangeIn.setValue(bpy.context.scene.frame_current)
    self.frameRangeIn.setMaximum(10000)
    self.frameRangeIn.valueChanged.connect(lambda : self.update_number())

    self.frameRangeOut = SpinBox()
    self.frameRangeOut.setValue(bpy.context.scene.frame_current)
    self.frameRangeOut.setMaximum(10000)
    self.frameRangeOut.valueChanged.connect(lambda : self.update_number())

    self.frameRangeLayout.addWidget(Label(text='Frame Range :'))
    self.frameRangeLayout.addWidget(self.frameRangeIn)
    self.frameRangeLayout.addWidget(self.frameRangeOut)

    #animation_step
    self.animationSettingsLayout = QHBoxLayout()
    self.step = SpinBox()
    self.step.setValue(2)
    self.step.setMinimum(1)
    self.step.valueChanged.connect(lambda : self.update_number())

    self.imgNumber = Label()
    self.imgNumber.setText(self.update_number())

    self.animationSettingsLayout.addWidget(Label(text='Step :'))
    self.animationSettingsLayout.addWidget(self.step)
    self.animationSettingsLayout.addWidget(Label(text='Number:'))
    self.animationSettingsLayout.addWidget(self.imgNumber)

    #option
    self.optionLayout = QHBoxLayout()
    self.only_selected = CheckBox('Selected Only')
    self.bezier = CheckBox('Bezier')
    self.mirror_pose = CheckBox('Mirror Pose')
    self.optionLayout.addWidget(self.only_selected)
    self.optionLayout.addWidget(self.bezier)
    self.optionLayout.addWidget(self.mirror_pose)


    #add to Main Layout
    self.mainLayout.addLayout(self.frameRangeLayout)
    self.mainLayout.addLayout(self.animationSettingsLayout)
    self.mainLayout.addLayout(self.optionLayout)



def store_acting(self):
    ob = bpy.context.scene.objects.active

    if ob.proxy_group :
        asset = ob.proxy_group.name
    else :
        asset = ob.name


    path = os.path.join(settings['path'],'animation_3d',asset,self.assetCategory.text(),self.assetName.text())
    image_path = os.path.join(path,self.assetName.text()+'_thumbnail.jpg')
    json_path = os.path.join(path,self.assetName.text()+'.json')

    action = store_anim(int(self.frameRangeIn.text()),int(self.frameRangeOut.text()),self.only_selected.isChecked(),self.bezier.isChecked(),self.mirror_pose.isChecked())

    write_anim(path,self.assetName.text(),action)

    asset_info={
        "asset" : self.assetName.text(),
        "type" : "acting",
        "image" : "./%s.jpg"%(self.assetName.text()+'_thumbnail'),
        "tags" : self.assetTags.text(),
        "path":"./%s.txt"%(self.assetName.text()+'_action'),
        "description" : self.assetDescription.toPlainText()
    }
    with open(json_path, 'w') as outfile:
        json.dump(asset_info, outfile)

    if self.previewImage.pixmap() :
        self.previewImage.pixmap().save(image_path, 'jpg',75)
