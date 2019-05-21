import bpy
import bmesh
from random import *
from bpy.props import *
import mathutils
import math
from mathutils import Vector
from bpy.types import Panel, UIList

# #########################################
# ViSP Property Panel
# #########################################

def update_after_enum(self, context):
    print('self.vp_model_types ---->', self.vp_model_types)

class IgnitProperties(bpy.types.PropertyGroup):
    vp_model_types = bpy.props.EnumProperty(
        name = "Type",
        description = "Model export types",
        items = [
            ("3D Faces" , "3D Faces" , "Export as 3d points"),
            ("3D Lines", "3D Lines", "Export as 3d lines"),
            ("3D Cylinders", "3D Cylinders", "Export as 3d cylinders"),
            ("3D Circles", "3D Circles", "Export as 3d circles")],
        update=update_after_enum
        )

    vp_line_face = BoolProperty(name = "Enable Face Export", description = "True or False?", default=True)

    vp_obj_Point1 = FloatVectorProperty(name = "", description = "Point 1 coordinate", size=3, default=[0.00,0.00,0.00])
    vp_obj_Point2 = FloatVectorProperty(name = "", description = "Point 2 coordinate", size=3, default=[0.00,0.00,0.00])
    vp_obj_Point3 = FloatVectorProperty(name = "", description = "Point 3 coordinate", size=3, default=[0.00,0.00,0.00])

    vp_radius = FloatProperty(name = "", default = 0,description = "Set radius")

class CustomProp_vertices(bpy.types.PropertyGroup):
    '''name = StringProperty() '''
    id = IntProperty()
    coord = FloatVectorProperty(description = "coordinate", size=3, default=[0.00,0.00,0.00])

class UL_items_vertices(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(0.3)
        split.label("%d" % (index))
        split.prop(item, "name", text="", emboss=False, translate=True)

    def invoke(self, context, event):
        pass  

class UIPanel(bpy.types.Panel):
    bl_label = "ViSP CAD Properites Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    def __init__(self):
        self._ob_select = None

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        col = layout.column()

        if not len(context.selected_objects):
            col.label("Select Object(s) in scene to add properties")
        #TODO: Add Tool Tip to buttons, set the LOD properties
        else:
            self._ob_select = context.selected_objects[0]
            try:
                self._ob_select["vp_model_types"]
            except:
                col.label("Add new property")
                col.operator("my.button", text="+ New").loc="ADD_NEW"

            else:
                # col.operator("refresh.button", text="load previous property") # Load prev. set properties. Button click required to write to panel
                col.prop(scn.ignit_panel, "vp_model_types", expand=False)
                col1 = col.column()
                col1.enabled = False

                if scn.ignit_panel.vp_model_types in ["3D Faces","3D Lines"]:
                    if context.active_object.mode == 'EDIT': # enable only in edit mode
                        col1.enabled = True
                    else:
                        col.label("Switch to EDIT MODE to get coordinates")
                        col.label("Note: Only needed if model is complex")

                    row3 = col1.row()
                    row3.operator("my.button", text="Show Normals").loc="SHOW_NORM"
                    row3.operator("my.button", text="Flip Normal").loc="FLIP_NORM"

                    col1.template_list("UL_items_vertices", "", scn, "custom_vertices", scn, "custom_vertices_index", rows=2)
                    row1 = col1.row()
                    row1.operator("my.button", text="Reduce Polycount").loc="LIM_DIS"
                    row1.operator("my.button", text="Get Vertices").loc="GET_VERTICES"
                    row1.operator("my.button", text="Clear List").number=7
                    if scn.ignit_panel.vp_model_types == "3D Lines":
                        col.prop(scn.ignit_panel, "vp_line_face")
                    bpy.app.debug = True

                elif scn.ignit_panel.vp_model_types in ["3D Cylinders","3D Circles"]:
                    if context.active_object.mode == 'EDIT': # enable only in edit mode
                        col1.enabled = True
                    else:
                        col.label("Switch to EDIT MODE to set radius and coordinates")

                    row3 = col1.row()
                    row3.operator("my.button", text="Show Normals").loc="SHOW_NORM"
                    row3.operator("my.button", text="Flip Normal").loc="FLIP_NORM"

                    if scn.ignit_panel.vp_model_types == "3D Circles":
                        col1.label("First point on circumference")
                        col1.prop(scn.ignit_panel, "vp_obj_Point1")
                        col1.label("Second point on circumference")
                        col1.prop(scn.ignit_panel, "vp_obj_Point2")
                        col1.label("Center point coordinate")
                        col1.prop(scn.ignit_panel, "vp_obj_Point3")

                    elif scn.ignit_panel.vp_model_types == "3D Cylinders":
                        col1.label("First point on revolution axis")
                        col1.prop(scn.ignit_panel, "vp_obj_Point1")
                        col1.operator("my.button", text="Update").loc="AXIS1"
                        col1.label("Second point on revolution axis")
                        col1.prop(scn.ignit_panel, "vp_obj_Point2")
                        col1.operator("my.button", text="Update").loc="AXIS2"

                    col1.label("Radius")
                    col1.prop(scn.ignit_panel, "vp_radius")
                    col1.operator("my.button", text="Update").loc="CAL_RAD"
                    col1.label("")
                    col1.operator("my.button", text="Clear Values").loc="CLEAR_VAL"

                col.label(" ")
                layout.operator("model_types.selection")
 
# #########################################
# BUTTON CALLS
# #########################################

new_mesh = ""
seed = ["b","l","e","n","d","r","v","t","i","s","p","a","z","y"]

def clear_vertices_list(scn):
    lst = scn.custom_vertices
    if len(lst) > 0:
        for i in range(len(lst)-1,-1,-1):
            scn.custom_vertices.remove(i)

def get_axis_point(selected):
    t = selected[1] - selected[0]
    u = selected[2] - selected[0]
    v = selected[2] - selected[1]
    w = mathutils.Vector.cross(t,u)
    len_w = math.pow(w[2],2) + math.pow(w[1],2) + math.pow(w[0],2)
    tt = t*t
    uu = u*u
    axis_pt = selected[0] + (u*tt*(u*v) - t*uu*(t*v))*0.5/len_w
    radius = math.sqrt(tt*uu*(v*v) * 0.25/len_w)
    return axis_pt, radius

def get_radius(selected):
    diff = selected[0] - selected[1]
    diameter = math.sqrt(math.pow(diff[0],2) + math.pow(diff[1],2) + math.pow(diff[2],2))
    return diameter/2

class OBJECT_OT_AddPropsButton(bpy.types.Operator):
    bl_idname = "model_types.selection"
    bl_label = "Add Properites"

    def execute(self, context):
        global new_mesh, seed
        scn = context.scene
        hasCircle = False
        hasCylinder = False
        ob = context.selected_objects[0]

        if scn.ignit_panel.vp_model_types == "3D Faces":
            ob["vp_model_types"] = scn.ignit_panel.vp_model_types
            attr=(o.name for o in scn.custom_faces)
            if ob.name not in attr:
                scn.custom_faces_index = len(scn.custom_faces)
                item = scn.custom_faces.add()
                item.id = len(scn.custom_faces)
                if len(scn.custom_vertices) > 0:
                    item.name = new_mesh
                else:
                    item.name = ob.name
            scn.custom_faces[scn.custom_faces_index].enabled = True
            clear_vertices_list(scn)

        elif scn.ignit_panel.vp_model_types == "3D Lines":
            ob["vp_model_types"] = scn.ignit_panel.vp_model_types
            ob["vp_line_face"] = scn.ignit_panel.vp_line_face
            attr=(o.name for o in scn.custom_lines)
            if ob.name not in attr:
                scn.custom_lines_index = len(scn.custom_lines)
                item = scn.custom_lines.add()
                item.id = len(scn.custom_lines)
                if len(scn.custom_vertices) > 0:
                    item.name = new_mesh
                else:
                    item.name = ob.name
            scn.custom_lines[scn.custom_lines_index].enabled = True
            clear_vertices_list(scn)

        elif scn.ignit_panel.vp_model_types in ["3D Cylinders","3D Circles"]:
            attr_circle = (o.name for o in scn.custom_circle)
            attr_cylinder = (o.name for o in scn.custom_cylinder)
            if ob.name not in attr_cylinder:
                hasCylinder = True
            if ob.name not in attr_circle:
                hasCircle = True

            if hasCircle and hasCylinder:
                shuffle(seed)
                me = bpy.data.meshes.new(scn.ignit_panel.vp_model_types + "_" + "".join(seed))
                ob = bpy.data.objects.new(scn.ignit_panel.vp_model_types + "_" + "".join(seed), me)
                scn.objects.link(ob)
                # scn.objects.active = ob
                # ob.select = True

            ob["vp_model_types"] = scn.ignit_panel.vp_model_types
            ob["vp_obj_Point1"] = scn.ignit_panel.vp_obj_Point1
            ob["vp_obj_Point2"] = scn.ignit_panel.vp_obj_Point2
            ob["vp_radius"] = scn.ignit_panel.vp_radius

            if scn.ignit_panel.vp_model_types == "3D Circles":
                ob["vp_obj_Point3"] = scn.ignit_panel.vp_obj_Point3
                if hasCircle:
                    scn.custom_circle_index = len(scn.custom_circle)
                    item = scn.custom_circle.add()
                    item.id = len(scn.custom_circle)
                    item.name = ob.name
                scn.custom_circle[scn.custom_circle_index].enabled = True
            else:
                if hasCylinder:
                    scn.custom_cylinder_index = len(scn.custom_cylinder)
                    item = scn.custom_cylinder.add()
                    item.id = len(scn.custom_cylinder)
                    item.name = ob.name
                scn.custom_cylinder[scn.custom_cylinder_index].enabled = True

        return{'FINISHED'}

class OBJECT_OT_Button(bpy.types.Operator):
    bl_idname = "my.button"
    bl_label = "Button"
    number = bpy.props.IntProperty()
    loc = bpy.props.StringProperty()

    def __init__(self):
        self._ob_select = None

    # @classmethod
    # def poll(cls, context):
    #     return (True)

    def execute(self, context):
        global new_mesh, seed
        scn = context.scene
        message_cy = "Select 1 point to update axis point;\nSelect 2 points to calculate only radius;\nSelect 3 points to calculate radius and axis point"
        message_cr = "Select 1 point to update center point;\nSelect 2 points to calculate radius;\nSelect 3 points to calculate radius and center point"

        if self.number == 7:
            clear_vertices_list(scn)

        elif self.loc == "ADD_NEW":
            self._ob_select = context.selected_objects[0]
            self._ob_select["vp_model_types"] = "3D Faces"# init

        elif self.loc == "CLEAR_VAL":
            scn.ignit_panel.vp_obj_Point1 = [0.00,0.00,0.00]
            scn.ignit_panel.vp_obj_Point2 = [0.00,0.00,0.00]
            scn.ignit_panel.vp_radius = 0.00
            if scn.ignit_panel.vp_model_types == "3D Circles":
                scn.ignit_panel.vp_obj_Point3 = [0.00,0.00,0.00]

        elif self.loc == "LIM_DIS":
            bpy.ops.mesh.dissolve_limited()

        elif self.loc == "SHOW_NORM":
            bpy.context.object.data.show_normal_face = True
            bpy.context.scene.tool_settings.normal_size = 0.5

        elif self.loc == "FLIP_NORM":
            bpy.context.object.data.show_normal_face = True
            bpy.ops.mesh.flip_normals()

        else:
            ob = context.selected_objects[0]
            ob_edit = context.edit_object # check if in edit mode
            me = ob_edit.data
            bm = bmesh.from_edit_mesh(me)
            ob_selected = [v for v in bm.verts if v.select]
            selected = []
            mat = ob.matrix_world

            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    if area.spaces[0].transform_orientation == 'GLOBAL':
                        for i in range(0,len(ob_selected)):
                            selected.append(mat * ob_selected[i].co)
                    else:
                        for i in range(0,len(ob_selected)):
                            selected.append(ob_selected[i].co)

            #Get selected vertices
            if self.loc == "GET_VERTICES":
                #TODO: update points
                for v in selected:
                    item = scn.custom_vertices.add()
                    item.id = len(scn.custom_vertices)
                    item.coord = [round(i,4) for i in v]
                    item.name = ",".join(map(str,[x for x in item.coord]))
                    scn.custom_vertices_index = (len(scn.custom_vertices)-1)

                #Separate the vertices to form a new mesh
                bpy.ops.mesh.separate(type='SELECTED')
                bpy.ops.object.mode_set(mode='OBJECT')
                for obj in scn.objects:
                    if obj.type == 'MESH' and obj.name == scn.objects[0].name:
                        scn.objects.active = obj
                        obj.select = True
                    else:
                        obj.select = False

                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='TOGGLE')
                # Fill missing faces.
                try:
                    bpy.ops.mesh.edge_face_add()
                except:
                    print("No missing faces detected")
                    pass
                # Apply Limited Dissove to reduce poly count to one.
                if len(bpy.context.object.data.polygons) > 1:
                    bpy.ops.mesh.dissolve_limited()

                shuffle(seed)
                scn.objects[0].name += scn.ignit_panel.vp_model_types + "_" + "".join(seed)
                new_mesh = scn.objects[0].name

            # Calculate/Set Axis Points
            elif self.loc == "AXIS1":
                if len(selected) == 1:
                    scn.ignit_panel.vp_obj_Point1 = selected[0]
                elif len(selected) == 3:
                    scn.ignit_panel.vp_obj_Point1, scn.ignit_panel.vp_radius = get_axis_point(selected)
                elif len(selected) == 0:
                    self.report({'ERROR'}, "No points selected!\n" + message_cy)
                else:
                    self.report({'ERROR'}, "Cannot update axis revolution point and radius from 2 or more than 3 points!\n" + message_cy)

            elif self.loc == "AXIS2":
                if len(selected) == 1:
                    scn.ignit_panel.vp_obj_Point2 = selected[0]
                elif len(selected) == 3:
                    scn.ignit_panel.vp_obj_Point2, scn.ignit_panel.vp_radius = get_axis_point(selected)
                elif len(selected) == 0:
                    self.report({'ERROR'}, "No points selected!\n" + message_cy)
                else:
                    self.report({'ERROR'}, "Cannot update axis revolution point and radius from 2 or more than 3 points!\n" + message_cy)

            # Calculate Radius
            elif self.loc == "CAL_RAD":
                if scn.ignit_panel.vp_model_types == "3D Circles":
                    if len(selected) == 1:
                        scn.ignit_panel.vp_obj_Point3 = selected[0]
                    elif len(selected) == 2:
                        scn.ignit_panel.vp_radius = get_radius(selected)
                    elif len(selected) == 3:
                        scn.ignit_panel.vp_obj_Point1 = selected[0]
                        scn.ignit_panel.vp_obj_Point2 = selected[1]
                        scn.ignit_panel.vp_obj_Point3, scn.ignit_panel.vp_radius = get_axis_point(selected)
                    else:
                        self.report({'ERROR'}, "Cannot update circle from 0 or more than 3 points!\n" + message_cr)

                elif scn.ignit_panel.vp_model_types == "3D Cylinders":
                    if len(selected) == 2:
                        scn.ignit_panel.vp_radius = get_radius(selected)
                    else:
                        self.report({'ERROR'}, "Cannot update radius when the number of selected points differ from 2.")

        return{'FINISHED'}

classes = (
    IgnitProperties,
    CustomProp_vertices,
    UIPanel,
    OBJECT_OT_Button,
    OBJECT_OT_AddPropsButton,
    UL_items_vertices
)

if __name__ == "__main__":
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
