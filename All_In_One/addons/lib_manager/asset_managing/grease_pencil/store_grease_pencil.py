from PyQt5.QtWidgets import QHBoxLayout,QVBoxLayout,QSpacerItem,QSizePolicy
#from PyQt5.QtCore
from PyQt5.QtGui import QPixmap,QIcon

from ...widgets import SpinBox,CheckBox,Label,LineEdit,ComboBox
from ...functions import read_json,get_css,icon_path

import bpy,os,json

working_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
settings = read_json(os.path.join(working_dir,"settings.json"))

def store_grease_pencil_settings(self):
    #Data Block
    self.gpDataBlock = ComboBox()
    self.gpDataBlock.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
    self.gpDataBlock.setStyleSheet(get_css("ComboBoxAsset"))
    for data_block in [gp.name for gp in bpy.data.grease_pencil]:
        self.gpDataBlock.addItem(QIcon(icon_path('ICON_GREASEPENCIL')), data_block)

    self.gpDataBlockRow = QHBoxLayout()
    self.gpDataBlockRow.addWidget(Label(text = 'Data Block :'))
    self.gpDataBlockRow.addWidget(self.gpDataBlock)

    self.mainLayout.addLayout(self.gpDataBlockRow)

    pass

def store_grease_pencil(self):
    path = os.path.join(settings['path'],'animation_2d',self.assetCategory.text(),self.assetName.text())
    image_path = os.path.join(path,self.assetName.text()+'_thumbnail.jpg')
    json_path = os.path.join(path,self.assetName.text()+'.json')
    gpencil_path = os.path.join(path,self.assetName.text()+'_gpencil.txt')

    gpencil_datablock = bpy.data.grease_pencil.get(self.gpDataBlock.currentText())

    gpencil={"layers":[],
                "palettes" : {}
    }

    for layer in gpencil_datablock.layers :
        layer_data ={
        "info" : layer.info,
        "show_x_ray" : layer.show_x_ray,
        "line_change" : layer.line_change,
        "hide" : layer.hide,
        "opacity" : layer.opacity,
        "parent" : layer.parent.name if layer.parent else '',
        "parent_type" : layer.parent_type,
        "parent_bone" : layer.parent_bone,
        "matrix_inverse" : [list(v) for v in layer.matrix_inverse],
        "strokes" : []
        }
        for i,stroke in enumerate(layer.active_frame.strokes) :
            stroke_data = {
            "line_width" : stroke.line_width,
            "draw_mode" : stroke.draw_mode,
            "points" : [],
            "palette" : stroke.colorname
            }
            for j,point in enumerate(stroke.points):
                point_data={
                "co" : list(point.co),
                "pressure" : point.pressure,
                "strength" : point.strength
                }
                stroke_data["points"].append(point_data)

            layer_data["strokes"].append(stroke_data)

        gpencil["layers"].append(layer_data)

    for palette in gpencil_datablock.palettes.active.colors :
        gpencil["palettes"][palette.name]={
        "color" : list(palette.color),
        "alpha" : palette.alpha,
        "fill_color" : list(palette.fill_color),
        "fill_alpha" : palette.fill_alpha
        }

    asset_info={
        "name" : self.assetName.text(),
        "type" : "GREASE_PENCIL",
        "image" : "./%s.jpg"%(self.assetName.text()+'_thumbnail'),
        "tags" : [1,2,3,4],
        "path":"./%s.txt"%(self.assetName.text()+'_gpencil'),
        "description" : "main character"
    }

    if not os.path.exists(path):
        os.makedirs(path)

    with open(json_path, 'w') as outfile:
        json.dump(asset_info, outfile)

    with open(gpencil_path, 'w') as outfile:
        json.dump(gpencil, outfile)

    if self.previewImage.pixmap() :
        self.previewImage.pixmap().save(image_path, 'jpg',75)

    print(gpencil)
