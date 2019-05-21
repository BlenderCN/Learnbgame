bl_info = \
{
    "name" : "Collapse Mesh Hierarchy",
    "author" : "Bronson Zgeb <bronson.zgeb@gmail.com>",
    "version" : (1, 0, 0),
    "blender" : (2, 6, 9),
    "location" : "",
    "description" : "Collapses the mesh hierarchy so that all objects with [Name].00X become a single object called [Name], unless they're texture mapped. This is to deal with Sketchup's bad exporter",
    "warning" : "",
    "wiki_url" : "",
    "tracker_url" : "",
    "category" : "3D View"
}

import re
import bpy

class CollapseMeshHierarchy(bpy.types.Operator):
    bl_idname = "mesh.collapse_hierarchy"
    bl_label = "Collapse Mesh Hierarchy"

    def deselect_all( self ):
        for item in bpy.context.selectable_objects:
            item.select = False

    def execute( self, context ):
        scene = bpy.context.scene
        # Grab the objects that don't end in .XXX where X is a number
        root_objs = [obj for obj in scene.objects if re.search( r'[^\.].{3}$', obj.name, re.M|re.I )]
        for root in root_objs:
            self.deselect_all()

            # All the objects with the same name
            obj_group = [obj for obj in scene.objects if obj.name.startswith( root.name + "." )]
            grouped_by_parent = {}

            for obj in obj_group:
                try:
                    parent_name = obj.parent.name
                except:
                    parent_name = "None"

                if parent_name not in grouped_by_parent:
                    grouped_by_parent[parent_name] = []

                if obj.type == 'MESH' and obj.active_material.active_texture is None:
                    grouped_by_parent[parent_name].append( obj )

            try:
                parent_name = root.parent.name
            except:
                parent_name = "None"
            if parent_name not in grouped_by_parent:
                grouped_by_parent[parent_name] = []
                
            if root.type == 'MESH' and root.active_material.active_texture is None:
                grouped_by_parent[parent_name].append( root )

            for key in grouped_by_parent:
                group = grouped_by_parent[key]
                if len(group) < 2:
                    continue
                    
                join_root = group[ len(group) - 1 ]
                if join_root is not None and len(group) > 1:
                    self.join_group( join_root, group )


        # root_objs = [obj for obj in scene.objects if re.search( r'[^\.].{3}$', obj.name, re.M|re.I )]
        # for root in root_objs:
        #     self.deselect_all()
        #     # Only grab objects at the same level in the hiearchy
        #     if root.parent is not None:
        #         child_objs = [obj for obj in root.parent.children if obj.name.startswith( root.name + "." )]
        #     else:
        #         child_objs = [obj for obj in scene.objects if obj.name.startswith( root.name + "." ) and obj.parent is None]
        #     if len(child_objs) < 1:
        #         continue
        #     if root.type != 'MESH':
        #         continue

            # self.join_group( root, child_objs )

        return {"FINISHED"}

    def join_group( self, root, group ):
        for child in group:
            if child.type == 'MESH' and child.active_material.active_texture is None:
                child.select = True
        root.select = True
        bpy.context.scene.objects.active = root
        bpy.ops.object.join()
        self.deselect_all()

def register():
    bpy.utils.register_class(CollapseMeshHierarchy)

def unregister():
    bpy.utils.unregister_class(CollapseMeshHierarchy)

if __name__ == "__main__":
    register()
