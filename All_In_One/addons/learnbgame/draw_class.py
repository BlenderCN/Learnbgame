
import os,sys
#import bpy

#path = os.path.join("./", "poqbdb")

path = os.path.join(os.path.dirname(__file__), "poqbdb")


level_dict = {0:[],1:[],2:[],3:[],4:[],5:[],6:[],7:[],8:[],9:[]}

classes = ["POQBDB_POQBDB","POQBDB_POQBDB_ADD","POQBDB_PROPERTY"]

gltf_dict = dict()


#def draw_classes():
for root,dirs,files in os.walk(path):
	level = root.replace(path,'').count(os.path.sep)
	#label = os.path.split(root)[-1]
	#print("root",root)
	level_dict[level].append(root.split(os.path.dirname(__file__)+os.path.sep)[1])
	if files:
		gltf_dict[root] = [os.path.splitext(gltf)[0] for gltf in files]

class_str = """import bpy\nimport os\nfrom bpy.types import (Panel,PropertyGroup,Operator)\n""" + \
"""from bl_ui.properties_object import ObjectButtonsPanel\n""" + \
"""from bpy.utils import previews\n""" +\
"""from bpy.props import (EnumProperty,PointerProperty)\n\n""" +\
"""icons_collection = {}\n\nicons = previews.new()\n""" +\
"""icons_dir = os.path.join(os.path.dirname(__file__), "icons")\n""" +\
"""icons_list = os.listdir(icons_dir)\n""" +\
"""for icon in os.listdir(icons_dir):\n\t""" +\
"""name, ext = os.path.splitext(icon)\n\t""" +\
"""icons.load(name, os.path.join(icons_dir, icon), 'IMAGE')\n""" +\
"""icons_collection["main"] = icons\n\n""" +\
"""class POQBDB_POQBDB(Panel):\n\tbl_label="poqbdb"\n\tbl_space_type = "VIEW_3D"\n\t""" +\
"""bl_region_type = "UI"\n\tbl_category = "Learnbgame"\n\t\n\n\tdef draw(self,context)""" + \
""":\n\t\tlayout=self.layout\n\t\tscene = context.scene\n\t\tpoqbdbs = scene.poqbdbs\n\t\t""" +\
"""row = layout.row()\n\t\trow.prop(poqbdbs,"poqbdb")\n\t\t""" +\
"""row.operator(POQBDB_POQBDB_ADD.bl_idname,text="add",icon="ADD")\n\n""" +\
"""class POQBDB_POQBDB_ADD(Operator):\n\tbl_idname = "poqbdb_poqbdb.add"\n\t""" +\
"""bl_label = "poqbdb_poqbdb+"\n\n\tdef execute(self,context):\n\t\t""" +\
"""poqbdbs = context.scene.poqbdbs\n\t\tother = poqbdbs.poqbdb\n\t\t""" + \
"""bpy.ops.import_scene.gltf(filepath=os.path.join(os.path.dirname(__file__),"{0}/") + other + ".glb")\n\t\t""".format(path)  + \
"""obj = context.selected_objects\n\t\tobj[0].name = other\n\t\t""" + \
"""obj[0].location = context.scene.cursor.location \n\t\treturn {'FINISHED'}""" +\
"""\n\n"""

for key,value in level_dict.items():
	for label_dir in value:
		label = os.path.split(label_dir)[-1]
		label_parent = os.path.split(label_dir)[-2].split(os.path.sep)[-1]
		if label_parent:
			classes.append(label_dir.replace(os.path.sep,"_").upper())
			classes.append(label_dir.replace(os.path.sep,"_").upper()+"_ADD")
			class_str += """class {0}(Panel,ObjectButtonsPanel):\n\t""".format(label_dir.replace(os.path.sep,"_").upper()) + \
			"""bl_label="{0}"\n\tbl_space_type = "VIEW_3D"\n\t""".format(label) + \
			"""bl_region_type = "UI"\n\tbl_category = "Learnbgame"\n\tbl_parent_id """ + \
			"""= "POQBDB_{0}"\n\n\tglobal icons_collection\n\ticons = icons_collection["main"]\n\n\tdef draw(self,context):\n\t\tlayout=""".format(label_parent.upper()) +\
			"""self.layout\n\t\tscene = context.scene\n\t\tpoqbdbs = scene.poqbdbs\n\t\t""" + \
			"""row = layout.row()\n\t\trow.prop(poqbdbs,"{0}",icon_value=icons[poqbdbs.{0} if poqbdbs.{0}+".png" in icons_list else "learnbgame"].icon_id)\n\t\t""".format(label_dir.replace(os.path.sep,"_")) +\
			"""row.operator({0}.bl_idname,text="add",icon="ADD")\n\n""".format(label_dir.replace(os.path.sep,"_").upper()+"_ADD") +\
			"""class {0}(Operator):\n\tbl_idname = "{1}.add"\n\t""".format(label_dir.replace(os.path.sep,"_").upper()+"_ADD",label_dir.replace(os.path.sep,"_")) +\
			"""bl_label = "{0}"\n\n\tdef execute(self,context):\n\t\t""".format(label_dir.replace(os.path.sep,"_")+"+") +\
			"""poqbdbs = context.scene.poqbdbs\n\t\t{0} = poqbdbs.{0}\n\t\t""".format(label_dir.replace(os.path.sep,"_")) + \
			"""bpy.ops.import_scene.gltf(filepath=os.path.join(os.path.dirname(__file__),"{0}")+os.path.sep + {1} + ".glb")\n\t\t""".format(label_dir,label_dir.replace(os.path.sep,"_"))  + \
			"""obj = context.selected_objects\n\t\tobj[0].name = {0}\n\t\t""".format(label_dir.replace(os.path.sep,"_")) + \
			"""obj[0].location = context.scene.cursor.location \n\t\treturn {'FINISHED'}\n\n""" 

class_str += """class POQBDB_PROPERTY(PropertyGroup):\n\t"""

for key,value in gltf_dict.items():

	class_str+="""{0} : EnumProperty(\n\t\tname="{1}",""".format(key.split(os.path.dirname(__file__)+os.path.sep)[1].replace(os.path.sep,"_"),os.path.split(key)[-1]) +\
	"""\n\t\titems=[\n\t\t\t"""
	for gltf in value:
		gltf_name = os.path.splitext(gltf)[0]
		class_str += """("{0}","{1}","add {2}"),\n\t\t\t""".format(gltf_name,gltf_name.capitalize(),gltf_name)
	class_str +="""]\n\t)\n\n\t"""

class_str += """\n\ndef register():"""
for cla in classes:
	class_str += """\n\tbpy.utils.register_class({0})\n\t""".format(cla) 

class_str += """\n\tbpy.types.Scene.poqbdbs = PointerProperty(type=POQBDB_PROPERTY)\n\ndef unregister():"""

for cla in classes:
	class_str += """\n\tbpy.utils.unregister_class({0})\n\t""".format(cla) 
sys.stdout = open(os.path.join(os.path.dirname(__file__),"poqbdb.py"),"w")
print(class_str)

"""
with open(os.path.join(os.path.dirname(__file__),"poqbdb.py"),"r+") as class_file:
	class_file.seek(0)
	class_file.truncate()
	class_file.close()



def register():
	class_bin = write_class(draw_classes())
	subprocess.call(class_bin)
	#poqbdb.register()

def unregister():
	poqbdb.unregister()

if __name__ == '__main__':
	draw_classes()
	#register()
"""

