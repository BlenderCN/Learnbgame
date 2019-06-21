# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

import bpy

class RoundedProfilePanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_RoundedProfile"
    bl_label = "Rounded Profile"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        o = context.object
        if o is None:
            return False
        if 'RoundedProfileProps' not in o:
            return False
        else:
            return True

    def draw(self, context):
        o = context.object
        try:
            if 'RoundedProfileProps' not in o:
                return
        except:
            return

        layout = self.layout
        if bpy.context.mode == 'EDIT_MESH':
            layout.label('Warning: Operator does not work in edit mode.', icon = 'ERROR')
        else:
            self.drawProperties(o, layout)

    def drawProperties(self, o, layout):
        properties = o.RoundedProfileProps[0]
        row = self.drawGeneralProperties(layout, properties)
        self.drawInfo(layout, properties, row)
        
    def drawGeneralProperties(self, layout, properties):
        row = layout.row()
        row.prop(properties, 'type')
        row = layout.row()
        row.prop(properties, 'drawMode')
        row = layout.row()
        row.prop(properties, 'coordSystem')
        return row
    
    def drawInfo(self, layout, properties, row):
        row = layout.row()
        totalSidesText = "Total sides = " + str(properties.totalSides)
        row.label(totalSidesText)

#############################################
class RoundedProfileDetailsPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_RoundedProfileDetails"
    bl_label = "Profile Details"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        o = context.object
        if o is None:
            return False
        if 'RoundedProfileProps' not in o:
            return False
        else:
            return True

    def draw(self, context):
        o = context.object
        try:
            if 'RoundedProfileProps' not in o:
                return
        except:
            return

        layout = self.layout
        if bpy.context.mode == 'EDIT_MESH':
            layout.label('Warning: Operator does not work in edit mode.', icon = 'ERROR')
        else:
            self.drawCornersMain(o, layout)

    def drawCornersMain(self, o, layout):
        properties = o.RoundedProfileProps[0]
        box = layout.box()

        row = box.row()
        row.label("General Settings")
        box, row = self.drawMasterCornerProperties(layout, properties, box)
        box = self.drawMasterConnection(layout, properties, box)
        row = box.row()
        row.prop(properties, 'connectionAutoAdjustEnabled')

        self.drawCornersAndConnections(layout, properties, box)


    def drawMasterCornerProperties(self, layout, properties, box):
        row = box.row()
        row.prop(properties, 'masterCornerEnabled')
        if properties.masterCornerEnabled:
            row.prop(properties, 'masterCornerFlipAngle')
            row = box.row()
            row.prop(properties, 'masterCornerRadius')
            row.prop(properties, 'masterCornerSides')
        return box, row

    def drawCornersAndConnections(self, layout, properties, box):
        numOfCorners = len(properties.corners)
        coordSystem = properties.coordSystem
        for id in range(0, numOfCorners):
            box = layout.box()
            self.addCornerToMenu(id, box, properties.corners[id], properties.masterCornerEnabled, coordSystem)
            if not properties.masterConnectionEnabled:
                if (properties.type == 'Polygon') or (properties.type == 'Chain') or (properties.type == 'Curve' and id < numOfCorners - 1):
                    box = layout.box()
                    self.addConnectionToMenu(id, box, properties.connections[id], numOfCorners)

    def addCornerToMenu(self, id, box, actualCorner, master, coordSystem):
        row = box.row()

        row.label("Corner " + str(id + 1))
        if not master:
            row.prop(actualCorner, 'flipAngle')
        row = box.row()

        self.addCoordsForCorner(actualCorner, coordSystem, row)

        if not master:
            row = box.row()
            row.prop(actualCorner, 'radius')
            row.prop(actualCorner, 'sides')

        row = box.row()
        op = row.operator("mesh.rounded_profile_remove_corner")
        op.cornerId = id
        op = row.operator("mesh.rounded_profile_add_corner")
        op.cornerId = id

    def addCoordsForCorner(self, corners, coordSystem, row):
        if coordSystem == 'XY':
            row.prop(corners, 'x')
            row.prop(corners, 'y')
        elif coordSystem == 'Angular':
            row.prop(corners, 'coordAngle')
            row.prop(corners, 'coordRadius')
#         elif coordSystem == 'DeltaXY':
#             row.prop(corners, 'dx')
#             row.prop(corners, 'dy')
#         elif coordSystem == 'DeltaAngular':
#             row.prop(corners, 'deltaCoordAngle')
#             row.prop(corners, 'deltaCoordRadius')

    def addConnectionToMenu(self, id, box, connections, numOfCorners):
        if id < numOfCorners:
            box.label("Connection " + str(id + 1) + "-" + str(id + 2))
        elif id == numOfCorners:
            box.label("Connection " + str(id + 1) + "-" + str(1))
        else:
            box.label("Chain Connection " + str(id))
        row = box.row()
        row.prop(connections, 'type', expand = True)

        row = box.row()
        row.prop(connections, 'inout', expand = True)

        if connections.type == 'Arc' :
            row = box.row()
            row.prop(connections, 'radius')
            row.prop(connections, 'sides')
            row = box.row()
            row.prop(connections, 'flipCenter')
            row.prop(connections, 'flipAngle')

    def drawMasterConnection(self, layout, properties, box):
        row = box.row()
        row.prop(properties, 'masterConnectionEnabled')
        if properties.masterConnectionEnabled:
            row = box.row()
            row.prop(properties, 'masterConnectionType', expand = True)
            row = box.row()
            row.prop(properties, 'masterConnectionInout', expand = True)
            if properties.masterConnectionType == 'Arc':

                row = box.row()
                row.prop(properties, 'masterConnectionRadius')
                row.prop(properties, 'masterConnectionSides')
                row = box.row()
                row.prop(properties, 'masterConnectionflipCenter')
                row.prop(properties, 'masterConnectionflipAngle')
        return box

