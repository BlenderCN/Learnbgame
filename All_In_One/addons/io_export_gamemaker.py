bl_info = {
        "name": "Export GameMaker: Studio 3D Model (.d3d,.gml as .txt)",
        "author": "Martin Crownover & JimmyBegg, Darknet ",
        "version": (1, 2),
        "blender": (2, 7, 3),
        "location": "File > Export",
        "description": "Export 3D Model for GameMaker: Studio",
        "warning": "",
        "wiki_url": "",
        "tracker_url": "",
        "category": "Learnbgame",
}

'''
Usage Notes:
Build your 3D model, select it, then go to File > Export > GameMaker Model (.gml(.txt), .d3d).
Set options as desired and export.
'''

import bpy
from bpy.props import *
import os
import time
import mathutils

def prepMesh(object, flippy):
        bneedtri = False
        scene = bpy.context.scene
        bpy.ops.object.mode_set(mode='OBJECT')
        for i in scene.objects: i.select = False
        object.select = True
        scene.objects.active = object

        print("Checking mesh if needs to convert quad to Tri...")
        object.data.update(calc_tessface=True)
        for face in object.data.tessfaces:
                if (len(face.vertices) > 3):
                        bneedtri = True
                        break

        bpy.ops.object.mode_set(mode='OBJECT')
        #moved copy operation here so we don't do anything irreversible to the existing model
        me_da = object.data.copy()
        me_ob = object.copy()
        #note two copy two types else it will use the current data or mesh
        me_ob.data = me_da
        bpy.context.scene.objects.link(me_ob) #link the object to the scene #current object location
        #moved this stuff outside the triangulate operation
        for i in scene.objects: i.select = False #deselect all objects
        me_ob.select = True
        scene.objects.active = me_ob #set the mesh object to current
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')

        if bneedtri == True:
                bpy.ops.mesh.quads_convert_to_tris()

        if flippy:
                bpy.ops.mesh.flip_normals()

        bpy.context.scene.update()
        bpy.ops.object.mode_set(mode='OBJECT') # set it in object
        bpy.ops.object.mode_set(mode='OBJECT') # set it in object

        return me_ob

def writeString(file, string):
    file.write(bytes(string, 'UTF-8'))

def do_export(context, props, filepath):
        ob = context.active_object
        me_ob = prepMesh(ob, props.flip_y)
        current_scene = context.scene
        apply_modifiers = props.apply_modifiers

        mesh = me_ob.to_mesh(current_scene, apply_modifiers, 'PREVIEW')
        basename = mesh.name.capitalize()

        if props.rot_x90:
                mesh.transform(mathutils.Matrix.Rotation(radians(90.0), 4, 'X'))

        if props.flip_y:
                mesh.transform(mathutils.Matrix.Scale(-1, 4, (0.0, 1.0, 0.0)))
                #normals get flipped in prepMesh

        mesh.transform(mathutils.Matrix.Scale(props.mod_scale, 4))
        file = open(filepath, "wb")

        if props.output_d3d: #if d3d is selected then output .d3d file

                writeString(file, '100\n')

                nlines = 2

                for face in mesh.tessfaces:
                        for index in face.vertices:
                                nlines+=1

                writeString(file, '%i\n' % (nlines))

                writeString(file, '0 4 0 0 0 0 0 0 0 0 0\n')

                if len(mesh.uv_textures) > 0:
                        uv_layer = mesh.tessface_uv_textures.active
                        for face in mesh.tessfaces:
                                faceUV = uv_layer.data[face.index]
                                i=0
                                for index in face.vertices:
                                        if len(face.vertices) == 3:
                                                vert = mesh.vertices[index]
                                                writeString(file, '8 ')
                                                writeString(file, '%.4f %.4f %.4f ' % (vert.co.x, vert.co.y, vert.co.z))
                                                writeString(file, '%.4f %.4f %.4f ' % (vert.normal.x, vert.normal.y, vert.normal.z))
                                                if props.flip_uvs:
                                                        writeString(file, '%.4f %.4f ' % (faceUV.uv[i][0], 1-faceUV.uv[i][1]))
                                                else:
                                                        writeString(file, '%.4f %.4f ' % (faceUV.uv[i][0], faceUV.uv[i][1]))
                                                writeString(file, '0 0\n')
                                                i+=1
                else:
                        uv_layer = mesh.tessface_uv_textures.active
                        for face in mesh.tessfaces:
                                for index in face.vertices:
                                        if len(face.vertices) == 3:
                                                vert = mesh.vertices[index]
                                                writeString(file, '6 ')
                                                writeString(file, '%.4f %.4f %.4f ' % (vert.co.x, vert.co.y, vert.co.z))
                                                writeString(file, '%.4f %.4f %.4f ' % (vert.normal.x, vert.normal.y, vert.normal.z))
                                                writeString(file, '0 0 0 0\n')

                writeString(file, '1 0 0 0 0 0 0 0 0 0 0')

        else:    #otherwise output gml

                writeString(file, 'temp = d3d_model_create();\nd3d_model_primitive_begin(temp,pr_trianglelist);\n')

                if len(mesh.uv_textures) > 0:
                        uv_layer = mesh.tessface_uv_textures.active
                        for face in mesh.tessfaces:
                                faceUV = uv_layer.data[face.index]
                                i=0
                                for index in face.vertices:
                                        if len(face.vertices) == 3:
                                                vert = mesh.vertices[index]
                                                writeString(file, 'd3d_model_vertex_normal_texture(temp, ')
                                                writeString(file, '%f, %f, %f, ' % (vert.co.x, vert.co.y, vert.co.z) )
                                                writeString(file, '%f, %f, %f, ' % (vert.normal.x, vert.normal.y, vert.normal.z) )
                                                if props.flip_uvs:
                                                        writeString(file, '%f, %f' % (faceUV.uv[i][0], 1-faceUV.uv[i][1]) )
                                                else:
                                                        writeString(file, '%f, %f' % (faceUV.uv[i][0], faceUV.uv[i][1]) )
                                                writeString(file, ');\n')
                                                i+=1
                else:
                        uv_layer = mesh.tessface_uv_textures.active
                        for face in mesh.tessfaces:
                                for index in face.vertices:
                                        if len(face.vertices) == 3:
                                                vert = mesh.vertices[index]
                                                writeString(file, 'd3d_model_vertex_normal(temp, ')
                                                writeString(file, '%f, %f, %f, ' % (vert.co.x, vert.co.y, vert.co.z) )
                                                writeString(file, '%f, %f, %f, ' % (vert.normal.x, vert.normal.y, vert.normal.z) )
                                                writeString(file, ');\n')

                writeString(file, 'd3d_model_primitive_end(temp);\nreturn temp;')

        file.flush()
        file.close()

        #delete the new copy now
        bpy.context.scene.objects.unlink(me_ob)
        #reselect the original object
        ob.select = True
        bpy.context.scene.objects.active = ob

        return True

bpy.types.Scene.output_d3d = BoolProperty(
    name        = "Save as .d3d",
    description = "Exports the model in .d3d format instead of .gml as .txt",
    default     = True)

###### EXPORT OPERATOR #######
class Export_gm3d(bpy.types.Operator):
	'''Exports the active Object as a GameMaker Model'''
	bl_idname = "export_object.txt"
	bl_label = "Export GameMaker: Studio 3D Model (.gml .d3d)"

	filename_ext = ""
	
	filepath = StringProperty(
		subtype='FILE_PATH',
		)
		
	filter_glob = StringProperty(
		default="*.d3d;*.gml;*txt",
		options={'HIDDEN'},
		)

	output_d3d = bpy.types.Scene.output_d3d
	
	apply_modifiers = BoolProperty(name="Apply Modifiers",
													description="Applies Modifiers to the Object before exporting",
													default=True)

	rot_x90 = BoolProperty(name="Rotate X by 90",
													description="Rotate 90 degrees around X to convert to Y-up",
													default=False)

	flip_y = BoolProperty(name="Flip Y Coordinates",
													description="Flips the Y coordinates of the object",
													default=True)

	flip_uvs = BoolProperty(name="Flip UV Vertically",
													description="Flips the UV coordinates on the Y axis",
													default=True)

	mod_scale = FloatProperty(name="Scale",
													description="Adjusts the scale of the model",
													default=1.0)

	@classmethod
	def poll(cls, context):
			return context.active_object.type in ['MESH', 'CURVE', 'SURFACE', 'FONT']

	def execute(self, context):
			start_time = time.time()
			print('\n_____START_____')
			props = self.properties
			filepath = self.filepath
			if self.output_d3d:
					filepath = bpy.path.ensure_ext(filepath, ".d3d")
			else:
					filepath = bpy.path.ensure_ext(filepath, ".gml")

			exported = do_export(context, props, filepath)

			message = ""
			if exported:
				print('finished export in %s seconds' %((time.time() - start_time)))
				print(filepath)
				message = "Finish Export! File Path=" + filepath
			else:
				message = "Fail to Export!"
			self.report({'ERROR', 'INFO'}, message)
			return {'FINISHED'}

	def invoke(self, context, event):
			wm = context.window_manager

			if True:
					# File selector
					wm.fileselect_add(self) # will run self.execute()
					return {'RUNNING_MODAL'}
			elif True:
					# search the enum
					wm.invoke_search_popup(self)
					return {'RUNNING_MODAL'}
			elif False:
					# Redo popup
					return wm.invoke_props_popup(self, event) #
			elif False:
					return self.execute(context)


### REGISTER ###
def menu_func(self, context):
    default_path = os.path.splitext(bpy.data.filepath)[0] + ".d3d"
    self.layout.operator(Export_gm3d.bl_idname, text="GameMaker: Studio Model Export (.gml .d3d)").filepath = default_path

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func)

if __name__ == "__main__":
    register()