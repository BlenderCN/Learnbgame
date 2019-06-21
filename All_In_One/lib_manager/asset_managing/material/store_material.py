import bpy,os,json,subprocess

from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtGui import QPixmap,QIcon
from ...widgets import CheckBox,ComboBox,Label
from ...functions import read_json,icon_path

working_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
settings = read_json(os.path.join(working_dir,"settings.json"))

def set_mat_name(self) :
    self.assetName.setText(self.data_block.currentText())

def store_material_settings(self):
    self.data_block_row = QHBoxLayout()
    self.data_block = ComboBox()
    #self.data_block.addItem('None')
    for mat in [m for m in bpy.data.materials if not m.library] :
        self.data_block.addItem(QIcon(icon_path('ICON_MATERIAL')), mat.name)
    self.data_block.currentIndexChanged.connect(lambda : set_mat_name(self))

    self.data_block_row.addWidget(Label(text = 'From existing :'))
    self.data_block_row.addWidget(self.data_block)

    self.mainLayout.addLayout(self.data_block_row)

    #option
    self.replace_asset = CheckBox('Replace Asset')
    self.move_in_lib = CheckBox('Move in Lib')

    self.replace_assetRow = QHBoxLayout()
    self.replace_assetRow.addWidget(self.replace_asset)
    self.replace_assetRow.addWidget(self.move_in_lib)

    self.mainLayout.addLayout(self.replace_assetRow)


def store_material(self):
    path = os.path.join(settings['path'],self.assetCategory.text(),self.assetName.text())
    image_path = os.path.join(path,self.assetName.text()+'_thumbnail.jpg')
    json_path = os.path.join(path,self.assetName.text()+'.json')
    blend_path = os.path.join(path,self.assetName.text()+'.blend')

    if not os.path.exists(path):
        os.makedirs(path)

    if self.move_in_lib.isChecked()  :
        datablock = set([bpy.data.materials.get(self.data_block.currentText())])

        bpy.data.libraries.write(blend_path,datablock)

        script_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),'create_group.py')

        #cmd = "%s -b %s --python %s -- %s %s"%(bpy.app.binary_path,str(blend_path),script_path,self.assetName.text(),blend_path)

        #subprocess.call(cmd)

        path = "./%s.blend"%(self.assetName.text())
    else:
        path = bpy.data.filepath

    asset_info={
        "type" : "material",
        "asset" : self.assetName.text(),
        "image" : "./%s.jpg"%(self.assetName.text()+'_thumbnail'),
        "tags" : self.assetTags.text(),
        "path": path,
        "description" : self.assetDescription.toPlainText()
    }
    with open(json_path, 'w') as outfile:
        json.dump(asset_info, outfile)

    if self.previewImage and self.previewImage.pixmap() :
        self.previewImage.pixmap().save(image_path, 'jpg',75)

    if self.replace_asset.isChecked() :
        scene = bpy.context.scene

        with bpy.data.libraries.load(blend_path, link=True) as (data_src, data_dst):
            data_dst.materials = [self.assetName.text()]

        mat = bpy.data.materials.get(self.assetName.text())
        mat.user_remap(data_dst.materials[0])
