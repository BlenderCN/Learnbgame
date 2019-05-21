import bpy

class SCENE_PT_OSM(bpy.types.Panel):
    '''OSM Panel'''
    bl_label = "OSM"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(self,context):
        if context.scene:
            return True

    def draw(self,context):
        from os import path
        osm = context.scene.osm
        layout = self.layout
        
        if osm.file!='':
            row = layout.row()
            row.label('File: '+path.basename(osm.file))
            row = layout.row()
            row.operator('scene.remove_osm')
            row = layout.row()
            if path.exists(osm.file):
                row.operator('scene.rebuild_osm')
            else:
                row.label('Warning: Cannot rebuild because OSM file has been removed!')
                
        row = layout.row()
        row.prop(osm,'traffic_direction')
        row = layout.row()
        row.prop(osm,'offset_step')

        row = layout.row()
        row.label('Geo-Bounds')
        box = layout.box()
        box.label('Lat: min %4.4f max %4.4f' % (osm.geo_bounds_lat[0],osm.geo_bounds_lat[1]))
        box.label('Lon: min %4.4f max %4.4f' % (osm.geo_bounds_lon[0],osm.geo_bounds_lon[1]))

class MATERIAL_PT_OSM(bpy.types.Panel):
    '''OSM Material Panel'''
    bl_label = "OSM"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(self,context):
        if context.material:
            return True

    def draw(self,context):
        osm = context.material.osm
        layout = self.layout

        box = layout.box()
        box.prop(osm,'base_type')
        if osm.base_type=='building':
            box.prop(osm,'building_part')
            if osm.building_part in ('facade','sloped_roof'):
                box.prop(osm,'building_levels')
                box.prop(osm,'building_level_height')
            if osm.building_part=='facade':
                box.prop(osm,'building_default_levels')
        elif osm.base_type=='trafficway':
            box.prop(osm,'lanes')
            box.prop(osm,'lane_width')
            box.prop(osm,'trafficway_sort')
        elif osm.base_type=='area':
            pass

        tags_layout(layout,osm)

class GROUP_PT_OSM(bpy.types.Panel):
    '''OSM Group Panel'''
    bl_label = "OSM"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(self,context):
        if context.object and object_in_group(context.object):
            return True

    def draw(self,context):
        groups = object_groups(context.object)
        layout = self.layout

        for group in groups:
            osm = group.osm
            row = layout.row()
            row.label('Group: %s' % group.name)
            box = layout.box()
            tags_layout(box,osm,group.name)

class OBJECT_PT_OSM(bpy.types.Panel):
    '''OSM Object Panel'''
    bl_label = "OSM"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(self,context):
        if context.object:
            return True

    def draw(self,context):
        osm = context.object.osm
        layout = self.layout

        if osm.id !='':
            row = layout.row()
            row.label('ID: '+osm.id)

        if osm.name!='':
            row = layout.row()
            row.label('Name: '+osm.name)

        if len(osm.tags)>0:
            row = layout.row()
            row.label('Tags')
            box = layout.box()
            for tag in osm.tags:
                box.label(tag.name+' = '+tag.value)

def tags_layout(layout,osm,group=None):
    row = layout.row()
    row.label('Tags')

    if group:
        op = row.operator('group.add_osm_tag').group = group
    else:
        row.operator('material.add_osm_tag')

    for i in range(0,len(osm.tags)):
        tag_box = layout.box()
        tag_box.prop(osm.tags[i],'name')
        tag_box.prop(osm.tags[i],'value')
        tag_box.prop(osm.tags[i],'priority')
        tag_box.prop(osm.tags[i],'mandatory')
        if group:
            op = tag_box.operator('group.remove_osm_tag')
            op.index = i
            op.group = group
        else:
            tag_box.operator('material.remove_osm_tag').index = i

    layout.separator()

def object_in_group(object):
    for group in bpy.data.groups:
        if object.name in group.objects:
            return True
    return False

def object_groups(object):
    groups = []
    for group in bpy.data.groups:
        if object.name in group.objects:
            groups.append(group)
    return groups

def register_ui():
    bpy.utils.register_class(SCENE_PT_OSM)
    bpy.utils.register_class(MATERIAL_PT_OSM)
    bpy.utils.register_class(GROUP_PT_OSM)
    bpy.utils.register_class(OBJECT_PT_OSM)

def unregister_ui():
    bpy.utils.unregister_class(SCENE_PT_OSM)
    bpy.utils.unregister_class(GROUP_PT_OSM)
    bpy.utils.unregister_class(OBJECT_PT_OSM)