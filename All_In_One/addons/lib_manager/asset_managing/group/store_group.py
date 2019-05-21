import bpy,os,json,subprocess

from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtGui import QPixmap,QIcon
from ...widgets import CheckBox,ComboBox,Label
from ...functions import read_json,icon_path

working_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
settings = read_json(os.path.join(working_dir,"settings.json"))

def applyTransform(obj):
    mat = obj.getMatrix()
    me = obj.getData(mesh=True)
    for v in me.verts:
        v.co = v.co*mat
    mat.identity()

def set_group_name(self) :
    if self.from_existing.currentText()!= 'None':
           self.assetName.setText(self.from_existing.currentText())

def store_group_settings(self):
    print(self.parent.treeWidget.currentItem().text(1))
    self.from_existing_row = QHBoxLayout()
    self.from_existing = ComboBox()
    self.from_existing.addItem('None')
    for group in [g for g in bpy.data.groups if not g.library] :
        self.from_existing.addItem(QIcon(icon_path('ICON_GROUP')), group.name)
    self.from_existing.currentIndexChanged.connect(lambda : set_group_name(self))

    self.from_existing_row.addWidget(Label(text = 'From existing :'))
    self.from_existing_row.addWidget(self.from_existing)

    self.mainLayout.addLayout(self.from_existing_row)

    #option
    self.replace_asset = CheckBox('Replace Asset')
    self.apply_scale = CheckBox('Apply Scale')

    self.replace_assetRow = QHBoxLayout()
    self.replace_assetRow.addWidget(self.replace_asset)
    self.replace_assetRow.addWidget(self.apply_scale)

    #add to Main Layout
    self.mainLayout.addLayout(self.replace_assetRow)


def store_group(self):

    path = os.path.join(settings['path'],self.assetCategory.text(),self.assetName.text())
    image_path = os.path.join(path,self.assetName.text()+'_thumbnail.jpg')
    json_path = os.path.join(path,self.assetName.text()+'.json')
    blend_path = os.path.join(path,self.assetName.text()+'.blend')

    if not os.path.exists(path):
        os.makedirs(path)

    if self.from_existing.currentText() == 'None' :
        datablock = set([ob for ob in bpy.context.scene.objects if ob.select])

        bpy.data.libraries.write(blend_path,datablock)

        script_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),'create_group.py')

        cmd = "%s -b %s --python %s -- %s %s"%(bpy.app.binary_path,str(blend_path),script_path,self.assetName.text(),blend_path)

        subprocess.call(cmd)

        path = "./%s.blend"%(self.assetName.text())
    else:
        path = bpy.data.filepath

    asset_info={
        "type" : "group",
        "asset" : self.assetName.text(),
        "image" : "./%s.jpg"%(self.assetName.text()+'_thumbnail'),
        "tags" : self.assetTags.text(),
        "path": path,
        "description" : self.assetDescription.toPlainText()
    }
    with open(json_path, 'w') as outfile:
        json.dump(asset_info, outfile)

    if self.previewImage.pixmap() :
        self.previewImage.pixmap().save(image_path, 'jpg',75)

    if self.replace_asset.isChecked() :
        scene = bpy.context.scene
        ob = scene.objects.active

        with bpy.data.libraries.load(blend_path, link=True) as (data_src, data_dst):
            data_dst.groups = [self.assetName.text()]

        empty = bpy.data.objects.new(self.assetName.text(),None)
        scene.objects.link(empty)
        empty.matrix_world = ob.matrix_world
        empty.dupli_type ='GROUP'
        empty.dupli_group = data_dst.groups[0]

        for o in [o for o in scene.objects if o.select] :
            bpy.data.objects.remove(o)
