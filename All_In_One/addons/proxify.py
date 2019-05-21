#Copyright (c) 2014 Toyofumi Fujiwara
#Released under the MIT license
#http://opensource.org/licenses/mit-license.php

import bpy

def proxify():
    import os

    objs = bpy.context.selected_objects
    proxyObjs = []

    # group name as base name of source file 
    o = objs[0]
    group_name = os.path.basename(o.library.filepath)
    g = bpy.data.groups.new(group_name)

    # hash parent relation
    suffix = "_proxy" # proxified object has string at suffix
    hash = {o.name + suffix : o.parent.name + suffix for o in objs if o.parent}

    # set proxy and group 
    for o in objs:
        bpy.context.scene.objects.active = o
        bpy.ops.object.proxy_make()
        o = bpy.context.object
        g.objects.link(o)
        proxyObjs.append(o)

    # set parents by hash
    proxyObjsHasName = [o for o in proxyObjs if o.name in hash]
    for o in proxyObjsHasName:
        print( o.name + " " + hash[o.name])
        c = bpy.data.objects[o.name]
        p = bpy.data.objects[hash[o.name]]

        bpy.ops.object.select_all(action='DESELECT') 
        c.select = True
        p.select = True
        bpy.context.scene.objects.active = p
        bpy.ops.object.parent_set()

################### add on setting section###########################
bl_info = {
    "name": "Proxify ",
    "category": "Object",
}

import bpy


class ProxifyWithGroup(bpy.types.Operator):
    """proxify selected object and assign group"""
    bl_idname = "proxify_with_group.comic"
    bl_label = "proxify with group"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):  
        proxify()
        return {'FINISHED'}


def register():
    bpy.utils.register_class(ProxifyWithGroup)


def unregister():
    bpy.utils.unregister_class(ProxifyWithGroup)


if __name__ == "__main__":
    register()