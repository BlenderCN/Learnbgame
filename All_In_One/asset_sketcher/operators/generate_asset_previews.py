import bpy
from math import radians,degrees
import os
from mathutils import Vector


class GenerateAssetPreview(bpy.types.Operator):
    bl_idname = "asset_sketcher.generate_asset_preview"
    bl_label = "Generate Asset Preview"
    bl_description = "Creates a thumbnail preview for all assets in asset list."
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True
    
    def get_parent_child_objects(self,obj,objs=[]):
        context = bpy.context
        
        if obj not in objs:
            objs.append(obj)    
        
        if obj.parent == None or obj.parent in objs:
            for child in obj.children:
                self.get_parent_child_objects(child,objs)
        elif obj.parent != None and obj.parent not in objs:
            self.get_parent_child_objects(obj.parent,objs)
                    
        return objs
    
    def get_object_median(self,context,obj):
        point = Vector((0,0,0))
        for coord in obj.bound_box:
            point += Vector(coord)
        point /= 8
        point = obj.matrix_world * point
        return point     
    
    def convert_group_instance(self,context,scene,obj):
        scene.objects.active = obj
        bpy.ops.object.duplicates_make_real(use_base_parent=False,use_hierarchy=False)
        for obj in context.selected_objects:
            if obj.type == "EMPTY" and obj.dupli_type == "NONE":
                bpy.data.objects.remove(obj,do_unlink=True)
        for obj in context.selected_objects:
            obj.data = obj.data.copy()        
        scene.objects.active = context.selected_objects[0]        
        bpy.ops.object.join()
        return context.active_object
    
    def arrange_objects(self,context,preview_scene,objs):
        distance = 0
        
        for obj in objs:
            dimension = max(obj.dimensions[0],obj.dimensions[1])    
            if dimension > distance:
                distance = dimension
            
        j = 0
        obj_count = len(objs)
        row_width = int(obj_count*.5+.5)
        for i,obj in enumerate(objs):
            if i%row_width == 0 and i > 0 and obj_count > 2:
                j += 1
            height_offset = obj.location - self.get_object_median(context,obj)
            linked_obj = obj.copy()
            if linked_obj.type != "EMPTY":
                linked_obj.data = obj.data.copy()
            preview_scene.objects.link(linked_obj)
            
            if linked_obj.type == "EMPTY":
                linked_obj.select = True
                preview_scene.objects.active = linked_obj
                self.convert_group_instance(context,preview_scene,linked_obj)    
            
            x_pos = (i%row_width)*distance
            if j%2 == 0:
                x_pos -= distance*.5
            y_pos = j*distance
            linked_obj.location = Vector([x_pos,y_pos,0]) + height_offset
            linked_obj.select = True
            preview_scene.objects.active = linked_obj
        bpy.ops.object.join()
        return context.active_object    
    
    def execute(self, context):
        if bpy.data.filepath == "":
            self.report({'INFO'},"File needs to be saved before thumbnails can be generated.")
            return{'FINISHED'}
        wm = context.window_manager
        
        path = os.path.dirname(bpy.data.filepath)
        prev_scene = context.scene
        
        ### get or generate preview scene
        if "preview_scene" not in bpy.data.scenes:
            bpy.data.scenes.new("preview_scene")
        preview_scene = bpy.data.scenes["preview_scene"]
        preview_scene.render.resolution_x = 96
        preview_scene.render.resolution_y = 96
        preview_scene.render.resolution_percentage = 100
        preview_scene.render.engine = prev_scene.render.engine
        preview_scene.cycles.samples = 10
        preview_scene.cycles.film_transparent = True

        ### get or generate camera track to empty
        if "preview_cam_empty" not in preview_scene.objects:
            if "preview_cam_empty" in bpy.data.objects:
                preview_cam_empty = bpy.data.objects["preview_cam_empty"]
            else:    
                preview_cam_empty = bpy.data.objects.new("preview_cam_empty",None)
            preview_scene.objects.link(preview_cam_empty)
        preview_cam_empty = bpy.data.objects["preview_cam_empty"]
        
        ### get or generate preview camera
        if "preview_cam" not in preview_scene.objects:
            if "preview_cam" not in bpy.data.cameras:
                bpy.data.cameras.new("preview_cam")
            cam_data = bpy.data.cameras["preview_cam"]
            if "preview_cam" not in bpy.data.objects:
                preview_cam = bpy.data.objects.new("preview_cam",cam_data)
            else:
                preview_cam = bpy.data.objects["preview_cam"]    
            preview_scene.objects.link(preview_cam)
        preview_cam = preview_scene.objects["preview_cam"]
        preview_cam.data.type = "ORTHO"
        preview_scene.camera = preview_cam
        preview_scene.render.alpha_mode = "TRANSPARENT"
        
        ### get or generate track to constraint
        if "Track To" not in preview_cam.constraints:
            track_to = preview_cam.constraints.new("TRACK_TO")
            track_to.name = "Track To"
        track_to = preview_cam.constraints["Track To"]
        track_to.up_axis = "UP_Y"
        track_to.track_axis = "TRACK_NEGATIVE_Z"
        track_to.target = preview_cam_empty
        
        ### get or generate preview light
        if "preview_light" not in preview_scene.objects:
            if "preview_light" not in bpy.data.lamps:
                bpy.data.lamps.new("preview_light","HEMI")
            light_data = bpy.data.lamps["preview_light"]
            if "preview_light" not in bpy.data.objects:
                preview_light = bpy.data.objects.new("preview_light",light_data)
            else:
                preview_light = bpy.data.objects["preview_light"]    
            preview_scene.objects.link(preview_light)
        preview_light = preview_scene.objects["preview_light"]
        preview_light.rotation_euler[0] = radians(25)
        preview_light.rotation_euler[2] = radians(80)
        
        ### get or generate preview world
        if "preview_world" not in bpy.data.worlds:
            preview_world = bpy.data.worlds.new("preview_world")
        preview_world = bpy.data.worlds["preview_world"]
        preview_world.use_sky_paper = True
        preview_world.use_sky_blend = True
        preview_scene.world = preview_world
        
        context.screen.scene = preview_scene
        
        ### run through all assets and render a thumbnail
        for i,asset in enumerate(wm.asset_sketcher.asset_list):
            #obj = bpy.data.objects[asset.name] if asset.name in bpy.data.objects else None
            if asset.type == "OBJECT":
                objs = [bpy.data.objects[asset.name]] if asset.name in bpy.data.objects else []
                objs = self.get_parent_child_objects(objs[0],[])
                for obj in objs:
                    linked_obj = obj.copy()
                    linked_obj.data = obj.data.copy()
                    preview_scene.objects.link(linked_obj)
                    linked_obj.select = True
                    preview_scene.objects.active = linked_obj
                bpy.ops.object.join()
                objs = [context.active_object]
            elif asset.type == "GROUP":
                objs = []
                for obj in asset.group_objects:
                    if obj.name in bpy.data.objects:
                        objs.append(bpy.data.objects[obj.name])
                objs = [self.arrange_objects(context,preview_scene,objs)]
            elif asset.type == "EMPTY":
                obj = bpy.data.objects[asset.name]
                instance = obj.copy()
                preview_scene.objects.link(instance)
                instance.select = True
                preview_scene.objects.active = instance
                instance = self.convert_group_instance(context,preview_scene,instance)
                objs = [instance]
            if len(objs) > 0:
                linked_obj = objs[0]
                linked_obj.location = [0,0,0]
                preview_scene.update()
                    
                obj_median = self.get_object_median(context,linked_obj)
                preview_cam_empty.location = obj_median
                preview_cam.location = [obj_median[0]+5,-10,obj_median[2]+5]
                
                preview_cam.data.ortho_scale = max(linked_obj.dimensions[0],linked_obj.dimensions[1],linked_obj.dimensions[2]) * 1.5
                
                preview_cam.rotation_euler[0] = radians(90)
                
                filename = os.path.basename(bpy.data.filepath.split(".blend")[0])+".thumbs"
                preview_scene.render.filepath = os.path.join(path,filename,asset.name+".png")
                context_override = context.copy()
                context_override["scene"] = preview_scene
                bpy.ops.render.render(context_override,write_still=True,use_viewport=True,scene="preview_scene")
            preview_scene.objects.unlink(linked_obj)
            
        context.screen.scene = prev_scene    
        bpy.data.scenes.remove(preview_scene,do_unlink=True)
        bpy.context.window_manager.asset_previews_loaded = False
        return {"FINISHED"}
        