import os

path = os.path.join(os.path.dirname(__file__), "poqbdb")

level_dict = {0:[],1:[],2:[],3:[],4:[],5:[],6:[],7:[],8:[],9:[]}


gltf_dict = dict()

for root,dirs,files in os.walk(path):
	level = root.replace(path,'').count(os.sep)
	#label = os.path.split(root)[-1]
	level_dict[level].append(root)
	if files:
		gltf_dict[root] = [os.path.splitext(gltf)[0] for gltf in files]
		if dirs:
			sub_label = dirs
			#print("sub",sub_label)
		#print(gltf_list)

#print(level_dict)
#print(gltf_dict)

class_str = """import bpy\nfrom bpy.types import Panel\n\n""" + \
"""class POQBDB_POQBDB(Panel):\n\tbl_label="poqbdb"\n\tbl_space_type = "VIEW_3D"\n\t""" +\
"""bl_region_type = "UI"\n\tbl_category = "Learnbgame"\n\t\n\n\tdef draw(self,context)""" + \
""":\n\t\tlayout=self.layout\n\t\tscene = context.scene\n\t\tpoqbdbs = scene.poqbdbs\n\t\t""" +\
"""row = layout.row()\n\t\trow.prop(poqbdbs,"poqbdbs")\n\n"""

for key,value in level_dict.items():
	for label_dir in value:
		label = os.path.split(label_dir)[-1]
		label_parent = os.path.split(label_dir)[-2].split("/")[-1]
		if label_parent:
			class_str += """class POQBDB_{0}(Panel):\n\t""".format(label.upper()) + \
			"""bl_label="{0}"\n\tbl_space_type = "VIEW_3D"\n\t""".format(label) + \
			"""bl_region_type = "UI"\n\tbl_category = "Learnbgame"\n\tbl_parent_id """ + \
			"""= "POQBDB_{0}"\n\n\tdef draw(self,context):\n\t\tlayout=""".format(label_parent.upper()) +\
			"""self.layout\n\t\tscene = context.scene\n\t\tpoqbdbs = scene.poqbdbs\n\t\t""" + \
			"""row = layout.row()\n\t\trow.prop(poqbdbs,"{0}")\n\n""".format(label) 

with open("poqbdb.py","w") as class_file:
	class_file.write(class_str)



