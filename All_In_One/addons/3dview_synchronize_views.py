# ##### BEGIN GPL LICENSE BLOCK #####
#
#  3dview_synchronize_views.py
#  3D Views synchronizator
#  Copyright (C) 2015 Quentin Wenger
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####



bl_info = {"name": "Synchronize 3D Views",
           "description": "Make orientations of 3D Views dependent of each other",
           "author": "Quentin Wenger (Matpi)",
           "version": (1, 0),
           "blender": (2, 74, 0),
           "location": "3D View(s) -> Properties -> Views Syncing",
           "warning": "",
           "wiki_url": "",
           "tracker_url": "",
           "category": "3D View"
           }



import bpy


def getCurrentWindowRegion(context):
    for region in context.area.regions:
        if region.type == 'WINDOW':
            return region

"""
def getWindowRegions(context):
    regions = []
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    regions.append(region)
                    break
    return regions
"""

def getWindowRegionsAndRegions3D(context):
    regions = []
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            region = None
            region_3d = None
            for item in area.regions:
                if item.type == 'WINDOW':
                    region = item
                    break
            for item in area.spaces:
                if item.type == 'VIEW_3D':
                    region_3d = item.region_3d
            regions.append((region, region_3d))
    return regions


def getWindowRegionsIDs(context):
    ids = []
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    ids.append(region.id)
                    break
    return ids



def syncViews(dummy):

    children_regions_3d = []
    parent_region_3d = None

    #for region in getWindowRegions(bpy.context):
    data = getWindowRegionsAndRegions3D(bpy.context)

    data_dict = dict((region.id, region_3d)
                     for region, region_3d in data)

    for prop in bpy.context.screen.view_sync_coll:
        region_3d = data_dict[prop.region_id]

        if prop.items == 'RECEIVE':
            children_regions_3d.append(region_3d)
        elif prop.items == 'SEND':
            parent_region_3d = region_3d

    if parent_region_3d is not None:
        for region_3d in children_regions_3d:
            region_3d.view_matrix = parent_region_3d.view_matrix



def updateSyncingStatus(self, context):
    # check for outdated region props and remove them
    ids = getWindowRegionsIDs(context)

    for prop in context.screen.view_sync_coll:
        if prop.region_id not in ids:
            context.screen.view_sync_coll.remove(prop)

    if self.items == 'SEND':
        # deactivate all other senders
        for prop in context.screen.view_sync_coll:
            if prop.region_id != self.region_id:
                if prop.items == 'SEND':
                    prop.items = 'NONE'

        # launch sync if needed
        if not syncViews in bpy.app.handlers.scene_update_pre:
            bpy.app.handlers.scene_update_pre.append(syncViews)

    else:
        # check for senders; if none found, stop sync
        # this is maybe not needed,
        # but could help a bit keeping good perfs
        for prop in context.screen.view_sync_coll:
            if prop.items == 'SEND':
                break
        else:
            if syncViews in bpy.app.handlers.scene_update_pre:
                bpy.app.handlers.scene_update_pre.remove(syncViews)
        


class ViewSyncingCollectionGroup(bpy.types.PropertyGroup):
    items = bpy.props.EnumProperty(
        items=[('NONE', "None", "No sync"),
               ('SEND', "Send", "Act as parent"),
               ('RECEIVE', "Receive", "Act as child")],
        default='NONE',
        update=updateSyncingStatus)
    region_id = bpy.props.IntProperty()



class ViewSyncingPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Views Syncing"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Views Syncing:")
        
        region_id = getCurrentWindowRegion(context).id

        index = None

        for i, item in enumerate(context.screen.view_sync_coll):
            if item.region_id == region_id:
                index = i
                layout.prop(
                    context.screen.view_sync_coll[index],
                    "items",
                    expand=True)
                break

        if index is None:
            prop = context.screen.view_sync_coll.add()
            prop.region_id = region_id
            layout.prop(
                prop,
                "items",
                expand=True)



def register():
    bpy.utils.register_module(__name__)
    bpy.types.Screen.view_sync_coll = bpy.props.CollectionProperty(
        type=ViewSyncingCollectionGroup)

def unregister():
    del bpy.types.Screen.view_sync_coll
    # to be sure...
    if syncViews in bpy.app.handlers.scene_update_pre:
        bpy.app.handlers.scene_update_pre.remove(syncViews)
    bpy.utils.unregister_module(__name__)
    

if __name__ == "__main__":
    register()
