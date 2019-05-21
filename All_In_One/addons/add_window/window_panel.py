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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

# PEP8 compliant (https://www.python.org/dev/peps/pep-0008)

# ----------------------------------------------------------
# File: window_panel.py
# Main panel for windows
# Author: Antonio Vazquez (antonioya)
#
# This code is base on the windows generator add-on created by SayProduction
# and has been adapted to continuous editing and cycles materials
#
# ----------------------------------------------------------
# noinspection PyUnresolvedReferences
import bpy
from window_tools import remove_doubles, set_normals, create_diffuse_material, create_glass_material
from math import pi, sin, cos, sqrt


def fitil(vr, fc, px, pz, x, y, z, zz, xx):
    k3 = z * 2
    vr.extend([[px[x] + xx, -z + zz, pz[y] + xx], [px[x] + xx + k3, -z + zz, pz[y] + xx + k3],
               [px[x] + xx + k3, z + zz, pz[y] + xx + k3], [px[x] + xx, z + zz, pz[y] + xx]])
    vr.extend([[px[x] + xx, -z + zz, pz[y + 1] - xx], [px[x] + xx + k3, -z + zz, pz[y + 1] - xx - k3],
               [px[x] + xx + k3, z + zz, pz[y + 1] - xx - k3], [px[x] + xx, z + zz, pz[y + 1] - xx]])
    vr.extend([[px[x + 1] - xx, -z + zz, pz[y + 1] - xx], [px[x + 1] - xx - k3, -z + zz, pz[y + 1] - xx - k3],
               [px[x + 1] - xx - k3, z + zz, pz[y + 1] - xx - k3], [px[x + 1] - xx, z + zz, pz[y + 1] - xx]])
    vr.extend([[px[x + 1] - xx, -z + zz, pz[y] + xx], [px[x + 1] - xx - k3, -z + zz, pz[y] + xx + k3],
               [px[x + 1] - xx - k3, z + zz, pz[y] + xx + k3], [px[x + 1] - xx, z + zz, pz[y] + xx]])
    n = len(vr)
    fc.extend([[n - 16, n - 15, n - 11, n - 12], [n - 15, n - 14, n - 10, n - 11], [n - 14, n - 13, n - 9, n - 10]])
    fc.extend([[n - 12, n - 11, n - 7, n - 8], [n - 11, n - 10, n - 6, n - 7], [n - 10, n - 9, n - 5, n - 6]])
    fc.extend([[n - 8, n - 7, n - 3, n - 4], [n - 7, n - 6, n - 2, n - 3], [n - 6, n - 5, n - 1, n - 2]])
    fc.extend([[n - 4, n - 3, n - 15, n - 16], [n - 3, n - 2, n - 14, n - 15], [n - 2, n - 1, n - 13, n - 14]])
    z = 0.005
    vr.extend([[px[x] + xx + k3, -z + zz, pz[y] + xx + k3], [px[x] + xx + k3, -z + zz, pz[y + 1] - xx - k3],
               [px[x + 1] - xx - k3, -z + zz, pz[y + 1] - xx - k3], [px[x + 1] - xx - k3, -z + zz, pz[y] + xx + k3]])
    vr.extend([[px[x] + xx + k3, z + zz, pz[y] + xx + k3], [px[x] + xx + k3, z + zz, pz[y + 1] - xx - k3],
               [px[x + 1] - xx - k3, z + zz, pz[y + 1] - xx - k3], [px[x + 1] - xx - k3, z + zz, pz[y] + xx + k3]])
    fc.extend([[n + 1, n + 0, n + 3, n + 2], [n + 4, n + 5, n + 6, n + 7]])


def kapak(vr, fc, px, pz, x, y, z, zz):
    k2 = z * 2
    vr.extend(
        [[px[x], -z + zz, pz[y]], [px[x] + k2, -z + zz, pz[y] + k2], [px[x] + k2, z + zz, pz[y] + k2],
         [px[x], z + zz, pz[y]]])
    vr.extend([[px[x], -z + zz, pz[y + 1]], [px[x] + k2, -z + zz, pz[y + 1] - k2], [px[x] + k2, z + zz, pz[y + 1] - k2],
               [px[x], z + zz, pz[y + 1]]])
    vr.extend(
        [[px[x + 1], -z + zz, pz[y + 1]], [px[x + 1] - k2, -z + zz, pz[y + 1] - k2],
         [px[x + 1] - k2, z + zz, pz[y + 1] - k2],
         [px[x + 1], z + zz, pz[y + 1]]])
    vr.extend([[px[x + 1], -z + zz, pz[y]], [px[x + 1] - k2, -z + zz, pz[y] + k2], [px[x + 1] - k2, z + zz, pz[y] + k2],
               [px[x + 1], z + zz, pz[y]]])
    n = len(vr)
    fc.extend([[n - 16, n - 15, n - 11, n - 12], [n - 15, n - 14, n - 10, n - 11], [n - 14, n - 13, n - 9, n - 10],
               [n - 13, n - 16, n - 12, n - 9]])
    fc.extend([[n - 12, n - 11, n - 7, n - 8], [n - 11, n - 10, n - 6, n - 7], [n - 10, n - 9, n - 5, n - 6],
               [n - 9, n - 12, n - 8, n - 5]])
    fc.extend([[n - 8, n - 7, n - 3, n - 4], [n - 7, n - 6, n - 2, n - 3], [n - 6, n - 5, n - 1, n - 2],
               [n - 5, n - 8, n - 4, n - 1]])
    fc.extend([[n - 4, n - 3, n - 15, n - 16], [n - 3, n - 2, n - 14, n - 15], [n - 2, n - 1, n - 13, n - 14],
               [n - 1, n - 4, n - 16, n - 13]])


# -----------------------------------------
# Set default values for each window type
# -----------------------------------------
def set_defaults(s):
    if s.prs == '1':
        s.gen = 3
        s.yuk = 1
        s.kl1 = 5
        s.kl2 = 5
        s.fk = 2
        s.gny0 = 190
        s.mr = True
        s.gnx0 = 60
        s.gnx1 = 110
        s.gnx2 = 60
        s.k00 = True
        s.k01 = False
        s.k02 = True
    if s.prs == '2':
        s.gen = 3
        s.yuk = 1
        s.kl1 = 5
        s.kl2 = 5
        s.fk = 2
        s.gny0 = 190
        s.mr = True
        s.gnx0 = 60
        s.gnx1 = 60
        s.gnx2 = 60
        s.k00 = True
        s.k01 = False
        s.k02 = True
    if s.prs == '3':
        s.gen = 3
        s.yuk = 1
        s.kl1 = 5
        s.kl2 = 5
        s.fk = 2
        s.gny0 = 190
        s.mr = True
        s.gnx0 = 55
        s.gnx1 = 50
        s.gnx2 = 55
        s.k00 = True
        s.k01 = False
        s.k02 = True
    if s.prs == '4':
        s.gen = 3
        s.yuk = 1
        s.kl1 = 5
        s.kl2 = 5
        s.fk = 2
        s.gny0 = 150
        s.mr = True
        s.gnx0 = 55
        s.gnx1 = 50
        s.gnx2 = 55
        s.k00 = True
        s.k01 = False
        s.k02 = True
    if s.prs == '5':
        s.gen = 3
        s.yuk = 1
        s.kl1 = 5
        s.kl2 = 5
        s.fk = 2
        s.gny0 = 150
        s.mr = True
        s.gnx0 = 50
        s.gnx1 = 40
        s.gnx2 = 50
        s.k00 = True
        s.k01 = False
        s.k02 = True
    if s.prs == '6':
        s.gen = 1
        s.yuk = 1
        s.kl1 = 5
        s.kl2 = 5
        s.fk = 2
        s.gny0 = 40
        s.mr = True
        s.gnx0 = 40
        s.k00 = False
    if s.prs == '7':
        s.gen = 1
        s.yuk = 2
        s.kl1 = 5
        s.kl2 = 5
        s.fk = 2
        s.gny0 = 195
        s.gny1 = 40
        s.gnx0 = 70
        s.k00 = True
        s.k10 = False
        s.mr = False
    if s.prs == '8':
        s.gen = 1
        s.yuk = 2
        s.kl1 = 5
        s.kl2 = 5
        s.fk = 2
        s.gny0 = 180
        s.gny1 = 35
        s.gnx0 = 70
        s.k00 = True
        s.k10 = False
        s.mr = False


# ------------------------------------------------------------------
# Define panel class for main functions.
# ------------------------------------------------------------------


class WindowMainPanel(bpy.types.Panel):
    bl_idname = "window_main_panel"
    bl_label = "Window"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "TOOLS"
    bl_category = 'Window'

    # ------------------------------
    # Draw UI
    # ------------------------------
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        row.operator("window.run_action", icon='MOD_LATTICE')
        row.prop(scene, "window_from")


# ------------------------------------------------------
# Button Action class
#
# ------------------------------------------------------


class RunAction(bpy.types.Operator):
    bl_idname = "window.run_action"
    bl_label = "Window"
    bl_description = "Create a Window with continuous editable parameters"

    # ------------------------------
    # Execute
    # ------------------------------
    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def execute(self, context):
        create_window()
        return {'FINISHED'}


# ------------------------------------------------------------------------------
# Create the window
# ------------------------------------------------------------------------------


def create_window():
    # deselect all objects
    for o in bpy.data.objects:
        o.select = False
    # Create main object
    window_mesh = bpy.data.meshes.new("Window")
    window_object = bpy.data.objects.new("Window", window_mesh)

    # Link object to scene
    bpy.context.scene.objects.link(window_object)
    window_object.WindowGenerator.add()

    # Shape the mesh.
    do_mesh(window_object)

    # Select, and activate object
    window_object.select = True
    bpy.context.scene.objects.active = window_object
    bpy.context.scene.objects.active.location = bpy.context.scene.cursor_location


# ------------------------------------------------------------------------------
# Update mesh of the window
# ------------------------------------------------------------------------------


# noinspection PyUnusedLocal
def update_window(self, context):
    # When update, the active object is the main object.
    o = bpy.context.active_object
    # Now deselect that object to not delete it.
    o.select = False
    # Remove data (mesh of active object),
    o.data.user_clear()
    bpy.data.meshes.remove(o.data)
    # and create a new mesh for the object:
    objmesh = bpy.data.meshes.new("Window")
    o.data = objmesh
    o.data.use_fake_user = True
    # deselect all objects
    for obj in bpy.data.objects:
        obj.select = False
    # Finally create all that again
    do_mesh(o, True)
    # and select, and activate, the object.
    o.select = True
    bpy.context.scene.objects.active = o


# ------------------------------------------------------------------------------
# Generate object
# For object, it only shapes mesh
# ------------------------------------------------------------------------------


# noinspection PyUnusedLocal
def do_mesh(myobject, update=False):
    op = myobject.WindowGenerator[0]
    # Create only mesh, because the object was created before.
    generate_window_object(op, myobject.data)

    # refine unit
    remove_doubles(myobject)
    set_normals(myobject)


# ------------------------------------------------------------------------------
# Update the parameters using a default value
# ------------------------------------------------------------------------------
# noinspection PyUnusedLocal
def update_using_default(self, context):
    o = context.object
    myobject = o.WindowGenerator[0]
    if myobject.son != myobject.prs:
        set_defaults(myobject)
        myobject.son = myobject.prs


# ------------------------------------------------------------------------------
# Generate window object
# ------------------------------------------------------------------------------


def generate_window_object(op, mymesh):
    myvertex = []
    myfaces = []

    ft1, cam, mer, sm = generate_vertex_data(op, myvertex, myfaces)

    mymesh.from_pydata(myvertex, [], myfaces)

    # Assign materials
    if op.mt1 == '1':
        mymesh.materials.append(create_diffuse_material("PVC", False, 1, 1, 1, 1, 1, 1))
    elif op.mt1 == '2':
        mymesh.materials.append(create_diffuse_material("Wood", False, 0.3, 0.2, 0.1, 0.3, 0.2, 0.1))
    elif op.mt1 == '3':
        mymesh.materials.append(create_diffuse_material("Plastic", False, 0, 0, 0, 0, 0, 0))
    if op.mt2 == '1':
        mymesh.materials.append(create_diffuse_material("PVC", False, 1, 1, 1, 1, 1, 1))
    elif op.mt2 == '2':
        mymesh.materials.append(create_diffuse_material("Wood", False, 0.3, 0.2, 0.1, 0.3, 0.2, 0.1))
    elif op.mt2 == '3':
        mymesh.materials.append(create_diffuse_material("Plastic", False, 0, 0, 0, 0, 0, 0))

    mymesh.materials.append(create_glass_material("Glass", False))
    if op.mr is True:
        mymesh.materials.append(create_diffuse_material("Marble", False, 0.9, 0.8, 0.7, 0.9, 0.8, 0.7))

    for i in ft1:
        mymesh.polygons[i].material_index = 1
    for i in cam:
        mymesh.polygons[i].material_index = 2
    for i in mer:
        mymesh.polygons[i].material_index = 3
    for i in sm:
        mymesh.polygons[i].use_smooth = 1

    mymesh.update(calc_edges=True)

    return


# -----------------------------------------
# Generate vertex and faces data
# -----------------------------------------
def generate_vertex_data(op, myvertex, myfaces):
    h1 = 0
    c = 0
    t1 = 0

    mx = op.gen
    my = op.yuk
    k1 = op.kl1 / 100
    k2 = op.kl2 / 100
    k3 = op.fk / 200
    res = op.res

    u = op.kl1 / 100
    xlist = [0, round(u, 2)]
    if mx > 0:
        u += op.gnx0 / 100
        xlist.append(round(u, 2))
        u += k2
        xlist.append(round(u, 2))
    if mx > 1:
        u += op.gnx1 / 100
        xlist.append(round(u, 2))
        u += k2
        xlist.append(round(u, 2))
    if mx > 2:
        u += op.gnx2 / 100
        xlist.append(round(u, 2))
        u += k2
        xlist.append(round(u, 2))
    if mx > 3:
        u += op.gnx3 / 100
        xlist.append(round(u, 2))
        u += k2
        xlist.append(round(u, 2))
    if mx > 4:
        u += op.gnx4 / 100
        xlist.append(round(u, 2))
        u += k2
        xlist.append(round(u, 2))
    if mx > 5:
        u += op.gnx5 / 100
        xlist.append(round(u, 2))
        u += k2
        xlist.append(round(u, 2))
    if mx > 6:
        u += op.gnx6 / 100
        xlist.append(round(u, 2))
        u += k2
        xlist.append(round(u, 2))
    if mx > 7:
        u += op.gnx7 / 100
        xlist.append(round(u, 2))
        u += k2
        xlist.append(round(u, 2))

    xlist[-1] = xlist[-2] + k1

    u = op.kl1 / 100
    zlist = [0, round(u, 2)]
    if my > 0:
        u += op.gny0 / 100
        zlist.append(round(u, 2))
        u += k2
        zlist.append(round(u, 2))
    if my > 1:
        u += op.gny1 / 100
        zlist.append(round(u, 2))
        u += k2
        zlist.append(round(u, 2))
    if my > 2:
        u += op.gny2 / 100
        zlist.append(round(u, 2))
        u += k2
        zlist.append(round(u, 2))
    if my > 3:
        u += op.gny3 / 100
        zlist.append(round(u, 2))
        u += k2
        zlist.append(round(u, 2))
    if my > 4:
        u += op.gny4 / 100
        zlist.append(round(u, 2))
        u += k2
        zlist.append(round(u, 2))
    zlist[-1] = zlist[-2] + k1

    u = xlist[-1] / 2
    for i in range(0, len(xlist)):
        xlist[i] -= u
    kx = [[op.k00, op.k10, op.k20, op.k30, op.k40],
          [op.k01, op.k11, op.k21, op.k31, op.k41],
          [op.k02, op.k12, op.k22, op.k32, op.k42],
          [op.k03, op.k13, op.k23, op.k33, op.k43],
          [op.k04, op.k14, op.k24, op.k34, op.k44],
          [op.k05, op.k15, op.k25, op.k35, op.k45],
          [op.k06, op.k16, op.k26, op.k36, op.k46],
          [op.k07, op.k17, op.k27, op.k37, op.k47]]
    cam = []
    mer = []
    ftl = []
    sm = []
    # -------------------------
    # VERTICES
    # -------------------------
    myvertex.extend([[xlist[0], -k1 / 2, zlist[0]], [xlist[0], k1 / 2, zlist[0]]])
    for x in range(1, len(xlist) - 1):
        myvertex.extend([[xlist[x], -k1 / 2, zlist[1]], [xlist[x], k1 / 2, zlist[1]]])
    myvertex.extend([[xlist[-1], -k1 / 2, zlist[0]], [xlist[-1], k1 / 2, zlist[0]]])
    for z in range(2, len(zlist) - 2, 2):
        for x in range(0, len(xlist)):
            myvertex.extend([[xlist[x], -k1 / 2, zlist[z]], [xlist[x], k1 / 2, zlist[z]]])
        for x in range(0, len(xlist)):
            myvertex.extend([[xlist[x], -k1 / 2, zlist[z + 1]], [xlist[x], k1 / 2, zlist[z + 1]]])
    z = len(zlist) - 2
    myvertex.extend([[xlist[0], -k1 / 2, zlist[z + 1]], [xlist[0], k1 / 2, zlist[z + 1]]])
    alt = []
    ust = [len(myvertex) - 2, len(myvertex) - 1]
    for x in range(1, len(xlist) - 1):
        myvertex.extend([[xlist[x], -k1 / 2, zlist[z]], [xlist[x], k1 / 2, zlist[z]]])
        alt.extend([len(myvertex) - 2, len(myvertex) - 1])
    myvertex.extend([[xlist[-1], -k1 / 2, zlist[z + 1]], [xlist[-1], k1 / 2, zlist[z + 1]]])
    son = [len(myvertex) - 2, len(myvertex) - 1]
    # -------------------------
    # FACES
    # -------------------------
    myfaces.append([0, 1, 3 + mx * 4, 2 + mx * 4])
    fb = [0]
    fr = [1]
    for i in range(0, mx * 4, 4):
        myfaces.append([i + 3, i + 2, i + 4, i + 5])
        fb.extend([i + 2, i + 4])
        fr.extend([i + 3, i + 5])
    fr.append(3 + mx * 4)
    fb.append(2 + mx * 4)
    fb.reverse()
    myfaces.extend([fb, fr])
    # Yatay
    y = (mx * 4 + 4)
    v = mx * 4 + 2
    for z in range(0, (my - 1) * y * 2, y * 2):
        myfaces.extend([[z + y + 1, z + y, z + y + 4 + mx * 4, z + y + 5 + mx * 4],
                        [z + y + v, z + y + v + 1, z + y + v + 5 + mx * 4, z + y + v + 4 + mx * 4]])
        for i in range(0, mx * 4 + 2, 2):
            myfaces.extend([[z + i + y + 0, z + i + y + 2, z + i + y + v + 4, z + i + y + v + 2],
                            [z + i + y + 3, z + i + y + 1, z + i + y + v + 3, z + i + y + v + 5]])
        for i in range(0, mx * 4 - 3, 4):
            myfaces.extend([[z + i + y + 2, z + i + y + 3, z + i + y + 5, z + i + y + 4],
                            [z + i + y + v + 5, z + i + y + v + 4, z + i + y + v + 6,
                             z + i + y + v + 7]])
    # Dikey
    for y in range(0, my):
        z = y * (mx * 4 + 4) * 2
        for i in range(0, mx * 4 + 2, 4):
            myfaces.extend([[z + i + 1, z + i + 0, z + i + v + 2, z + i + v + 3],
                            [z + i + 3, z + i + 1, z + i + v + 3, z + i + v + 5],
                            [z + i + 2, z + i + 3, z + i + v + 5, z + i + v + 4],
                            [z + i + 0, z + i + 2, z + i + v + 4, z + i + v + 2]])
    # Fitil
    if op.UST == '1':
        y1 = my
    else:
        y1 = my - 1
    for y in range(0, y1):
        for x in range(0, mx):
            if kx[x][y] is True:
                kapak(myvertex, myfaces, xlist, zlist, x * 2 + 1, y * 2 + 1, k2 / 2, (k1 + k2) * 0.5 - 0.01)
                fitil(myvertex, myfaces, xlist, zlist, x * 2 + 1, y * 2 + 1, k3, (k1 + k2) * 0.5 - 0.01, k2)
            else:
                fitil(myvertex, myfaces, xlist, zlist, x * 2 + 1, y * 2 + 1, k3, 0, 0)
            m = len(myfaces)
            cam.extend([m - 1, m - 2])
            ftl.extend([m - 3, m - 4, m - 5, m - 6, m - 7, m - 8, m - 9, m - 10, m - 11, m - 12, m - 13, m - 14])
    # -----------------------------------------------------
    if op.UST == '1':  # Duz
        myfaces.append([ust[1], ust[0], son[0], son[1]])
        for i in range(0, mx * 4, 4):
            myfaces.append([alt[i], alt[i + 1], alt[i + 3], alt[i + 2]])
        on = [ust[0]]
        ar = [ust[1]]
        for i in range(0, len(alt) - 1, 2):
            on.append(alt[i])
            ar.append(alt[i + 1])
        on.append(son[0])
        myfaces.append(on)
        ar.append(son[1])
        ar.reverse()
        myfaces.append(ar)
    elif op.UST == '2':  # Yay
        if op.DT2 == '1':
            h1 = op.VL1 / 100
            if h1 < 0.01:
                h1 = 0.01
                op.VL1 = 1
            elif h1 >= u:
                h1 = u - 0.01
                op.VL1 = h1 * 100
            h = sqrt(u ** 2 + h1 ** 2) / 2
            e = h * (u / h1)
            c = sqrt(h ** 2 + e ** 2)
            t1 = zlist[-1] - h1
        elif op.DT2 == '2':
            c = op.VL2 / 100
            if c < u + 0.01:
                c = u + 0.01
                op.VL2 = c * 100
            t1 = sqrt(c ** 2 - u ** 2) + zlist[-1] - c
        r = c - k1
        z = zlist[-1] - c

        myvertex[ust[0]][2] = t1
        myvertex[ust[1]][2] = t1
        myvertex[son[0]][2] = t1
        myvertex[son[1]][2] = t1
        for i in alt:
            myvertex[i][2] = sqrt(r ** 2 - myvertex[i][0] ** 2) + z

        on = [son[0]]
        u1 = []
        for i in range(0, res):
            a = i * pi / res
            x = cos(a) * c
            if -u < x < u:
                myvertex.append([x, -k1 / 2, sin(a) * c + z])
                on.append(len(myvertex) - 1)
        u1.extend(on)
        u1.append(ust[0])
        on.extend([ust[0], alt[0]])
        ar = []
        d1 = []
        d2 = []
        for i in range(0, len(alt) - 2, 4):
            x1 = myvertex[alt[i + 0]][0]
            x2 = myvertex[alt[i + 2]][0]
            on.append(alt[i + 0])
            ar.append(alt[i + 1])
            t1 = [alt[i + 0]]
            t2 = [alt[i + 1]]
            for j in range(0, res):
                a = j * pi / res
                x = -cos(a) * r
                if x1 < x < x2:
                    myvertex.extend([[x, -k1 / 2, sin(a) * r + z], [x, k1 / 2, sin(a) * r + z]])
                    on.append(len(myvertex) - 2)
                    ar.append(len(myvertex) - 1)
                    t1.append(len(myvertex) - 2)
                    t2.append(len(myvertex) - 1)
            on.append(alt[i + 2])
            ar.append(alt[i + 3])
            t1.append(alt[i + 2])
            t2.append(alt[i + 3])
            d1.append(t1)
            d2.append(t2)
        ar.append(son[1])
        u2 = [son[1]]
        for i in range(0, res):
            a = i * pi / res
            x = cos(a) * c
            if -u < x < u:
                myvertex.append([x, k1 / 2, sin(a) * c + z])
                ar.append(len(myvertex) - 1)
                u2.append(len(myvertex) - 1)
        ar.append(ust[1])
        u2.append(ust[1])
        ar.reverse()
        myfaces.extend([on, ar])
        for i in range(0, len(u1) - 1):
            myfaces.append([u1[i + 1], u1[i], u2[i], u2[i + 1]])
            sm.append(len(myfaces) - 1)
        for a in range(0, mx):
            for i in range(0, len(d1[a]) - 1):
                myfaces.append([d1[a][i + 1], d1[a][i], d2[a][i], d2[a][i + 1]])
                sm.append(len(myfaces) - 1)
        y = my - 1
        for x in range(0, mx):
            if kx[x][y] is True:
                fr = (k1 + k2) * 0.5 - 0.01
                ek = k2
                r = c - k1
                k = r - k2

                x1 = xlist[x * 2 + 1]
                x2 = xlist[x * 2 + 2]
                myvertex.extend([[x2, fr - k2 / 2, z + 1], [x2 - k2, fr - k2 / 2, z + 1],
                                 [x2 - k2, fr + k2 / 2, z + 1],
                                 [x2, fr + k2 / 2, z + 1]])
                myvertex.extend([[x2, fr - k2 / 2, zlist[-3]], [x2 - k2, fr - k2 / 2, zlist[-3] + k2],
                                 [x2 - k2, fr + k2 / 2,
                                  zlist[-3] + k2],
                                 [x2, fr + k2 / 2, zlist[-3]]])
                myvertex.extend([[x1, fr - k2 / 2, zlist[-3]], [x1 + k2, fr - k2 / 2, zlist[-3] + k2],
                                 [x1 + k2, fr + k2 / 2,
                                  zlist[-3] + k2],
                                 [x1, fr + k2 / 2, zlist[-3]]])
                myvertex.extend([[x1, fr - k2 / 2, z + 1], [x1 + k2, fr - k2 / 2, z + 1],
                                 [x1 + k2, fr + k2 / 2, z + 1],
                                 [x1, fr + k2 / 2, z + 1]])

                n = len(myvertex)
                myfaces.extend([[n - 16, n - 15, n - 11, n - 12], [n - 15, n - 14, n - 10, n - 11],
                                [n - 14, n - 13, n - 9, n - 10], [n - 13, n - 16, n - 12, n - 9]])
                myfaces.extend(
                    [[n - 12, n - 11, n - 7, n - 8], [n - 11, n - 10, n - 6, n - 7], [n - 10, n - 9, n - 5, n - 6],
                     [n - 9, n - 12, n - 8, n - 5]])
                myfaces.extend(
                    [[n - 8, n - 7, n - 3, n - 4], [n - 7, n - 6, n - 2, n - 3], [n - 6, n - 5, n - 1, n - 2],
                     [n - 5, n - 8, n - 4, n - 1]])
                alt = [n - 16, n - 15, n - 14, n - 13, n - 4, n - 3, n - 2, n - 1]
                myvertex[alt[0]][2] = sqrt(r ** 2 - myvertex[alt[0]][0] ** 2) + z
                myvertex[alt[1]][2] = sqrt(k ** 2 - myvertex[alt[1]][0] ** 2) + z
                myvertex[alt[2]][2] = sqrt(k ** 2 - myvertex[alt[2]][0] ** 2) + z
                myvertex[alt[3]][2] = sqrt(r ** 2 - myvertex[alt[3]][0] ** 2) + z
                myvertex[alt[4]][2] = sqrt(r ** 2 - myvertex[alt[4]][0] ** 2) + z
                myvertex[alt[5]][2] = sqrt(k ** 2 - myvertex[alt[5]][0] ** 2) + z
                myvertex[alt[6]][2] = sqrt(k ** 2 - myvertex[alt[6]][0] ** 2) + z
                myvertex[alt[7]][2] = sqrt(r ** 2 - myvertex[alt[7]][0] ** 2) + z

                d1 = []
                d2 = []
                t1 = []
                t2 = []
                for i in range(0, res):
                    a = i * pi / res
                    y1 = cos(a) * r
                    y2 = -cos(a) * k
                    if x1 < y1 < x2:
                        myvertex.extend([[y1, fr - k2 / 2, sin(a) * r + z], [y1, fr + k2 / 2, sin(a) * r + z]])
                        t1.append(len(myvertex) - 2)
                        t2.append(len(myvertex) - 1)
                    if x1 + k2 < y2 < x2 - k2:
                        myvertex.extend([[y2, fr - k2 / 2, sin(a) * k + z], [y2, fr + k2 / 2, sin(a) * k + z]])
                        d1.append(len(myvertex) - 2)
                        d2.append(len(myvertex) - 1)
                on = [alt[1], alt[0]]
                on.extend(t1)
                on.extend([alt[4], alt[5]])
                on.extend(d1)
                ar = [alt[2], alt[3]]
                ar.extend(t2)
                ar.extend([alt[7], alt[6]])
                ar.extend(d2)
                ar.reverse()

                if d1 == [] and t1 == []:
                    myfaces.extend([on, ar, [alt[5], alt[6], alt[2], alt[1]], [alt[7], alt[4], alt[0], alt[
                        3]]])
                    m = len(myfaces)
                    sm.extend(
                        [m - 1, m - 2])
                elif d1 == [] and t1 != []:
                    myfaces.extend([on, ar, [alt[5], alt[6], alt[2], alt[1]], [alt[7], alt[4], t1[-1], t2[-1]],
                                    [alt[0], alt[3], t2[0], t1[0]]])
                    m = len(myfaces)
                    sm.extend(
                        [m - 1, m - 2, m - 3])
                elif d1 != [] and t1 == []:
                    myfaces.extend([on, ar, [alt[5], alt[6], d2[0], d1[0]], [alt[2], alt[1], d1[-1], d2[-1]],
                                    [alt[7], alt[4], alt[0], alt[3]]])
                    m = len(myfaces)
                    sm.extend(
                        [m - 1, m - 2, m - 3])
                else:
                    myfaces.extend([on, ar, [alt[5], alt[6], d2[0], d1[0]], [alt[2], alt[1], d1[-1], d2[-1]],
                                    [alt[7], alt[4], t1[-1], t2[-1]], [alt[0], alt[3], t2[0], t1[0]]])
                    m = len(myfaces)
                    sm.extend(
                        [m - 1, m - 2, m - 3, m - 4])

                for i in range(0, len(d1) - 1):
                    myfaces.append([d1[i + 1], d1[i], d2[i], d2[i + 1]])
                    sm.append(len(myfaces) - 1)
                for i in range(0, len(t1) - 1):
                    myfaces.append([t1[i + 1], t1[i], t2[i], t2[i + 1]])
                    sm.append(len(myfaces) - 1)
                r = c - k1 - k2
                k = r - k3 * 2
            else:
                fr = 0
                ek = 0
                r = c - k1
                k = r - k3 * 2
            # Fitil
            x1 = xlist[x * 2 + 1] + ek
            x2 = xlist[x * 2 + 2] - ek
            myvertex.extend([[x2, fr - k3, z + 1], [x2 - k3 * 2, fr - k3, z + 1], [x2 - k3 * 2, fr + k3, z + 1],
                             [x2, fr + k3, z + 1]])
            myvertex.extend([[x2, fr - k3, zlist[-3] + ek], [x2 - k3 * 2, fr - k3, zlist[-3] + ek + k3 * 2],
                             [x2 - k3 * 2, fr + k3, zlist[-3] + ek + k3 * 2], [x2, fr + k3, zlist[-3] + ek]])
            myvertex.extend([[x1, fr - k3, zlist[-3] + ek], [x1 + k3 * 2, fr - k3, zlist[-3] + ek + k3 * 2],
                             [x1 + k3 * 2, fr + k3, zlist[-3] + ek + k3 * 2], [x1, fr + k3, zlist[-3] + ek]])
            myvertex.extend([[x1, fr - k3, z + 1], [x1 + k3 * 2, fr - k3, z + 1], [x1 + k3 * 2, fr + k3, z + 1],
                             [x1, fr + k3, z + 1]])
            n = len(myvertex)
            myfaces.extend(
                [[n - 16, n - 15, n - 11, n - 12], [n - 15, n - 14, n - 10, n - 11], [n - 14, n - 13, n - 9, n - 10]])
            myfaces.extend(
                [[n - 12, n - 11, n - 7, n - 8], [n - 11, n - 10, n - 6, n - 7], [n - 10, n - 9, n - 5, n - 6]])
            myfaces.extend([[n - 8, n - 7, n - 3, n - 4], [n - 7, n - 6, n - 2, n - 3], [n - 6, n - 5, n - 1, n - 2]])
            m = len(myfaces)
            ftl.extend([m - 1, m - 2, m - 3, m - 4, m - 5, m - 6, m - 7, m - 8, m - 9])
            alt = [n - 16, n - 15, n - 14, n - 13, n - 4, n - 3, n - 2, n - 1]
            myvertex[alt[0]][2] = sqrt(r ** 2 - myvertex[alt[0]][0] ** 2) + z
            myvertex[alt[1]][2] = sqrt(k ** 2 - myvertex[alt[1]][0] ** 2) + z
            myvertex[alt[2]][2] = sqrt(k ** 2 - myvertex[alt[2]][0] ** 2) + z
            myvertex[alt[3]][2] = sqrt(r ** 2 - myvertex[alt[3]][0] ** 2) + z
            myvertex[alt[4]][2] = sqrt(r ** 2 - myvertex[alt[4]][0] ** 2) + z
            myvertex[alt[5]][2] = sqrt(k ** 2 - myvertex[alt[5]][0] ** 2) + z
            myvertex[alt[6]][2] = sqrt(k ** 2 - myvertex[alt[6]][0] ** 2) + z
            myvertex[alt[7]][2] = sqrt(r ** 2 - myvertex[alt[7]][0] ** 2) + z
            d1 = []
            d2 = []
            t1 = []
            t2 = []
            for i in range(0, res):
                a = i * pi / res
                y1 = cos(a) * r
                y2 = -cos(a) * k
                if x1 < y1 < x2:
                    myvertex.extend([[y1, fr - k3, sin(a) * r + z], [y1, fr + k3, sin(a) * r + z]])
                    t1.append(len(myvertex) - 2)
                    t2.append(len(myvertex) - 1)
                    ftl.extend([len(myfaces) - 1, len(myfaces) - 2])
                if x1 + k3 * 2 < y2 < x2 - k3 * 2:
                    myvertex.extend([[y2, fr - k3, sin(a) * k + z], [y2, fr + k3, sin(a) * k + z]])
                    d1.append(len(myvertex) - 2)
                    d2.append(len(myvertex) - 1)
                    ftl.extend([len(myfaces) - 1, len(myfaces) - 2])
            on = [alt[1], alt[0]]
            on.extend(t1)
            on.extend([alt[4], alt[5]])
            on.extend(d1)
            ar = [alt[2], alt[3]]
            ar.extend(t2)
            ar.extend([alt[7], alt[6]])
            ar.extend(d2)
            ar.reverse()

            if not d1:
                myfaces.extend([on, ar, [alt[5], alt[6], alt[2], alt[1]]])
                m = len(myfaces)
                ftl.extend([m - 1, m - 2, m - 3])
                sm.extend([m - 1])
            else:
                myfaces.extend([on, ar, [alt[5], alt[6], d2[0], d1[0]], [alt[2], alt[1], d1[-1], d2[-1]]])
                m = len(myfaces)
                ftl.extend([m - 1, m - 2, m - 3, m - 4])
                sm.extend([m - 1, m - 2])

            for i in range(0, len(d1) - 1):
                myfaces.append([d1[i + 1], d1[i], d2[i], d2[i + 1]])
                ftl.append(len(myfaces) - 1)
                sm.append(len(myfaces) - 1)
            # Cam
            x1 = xlist[x * 2 + 1] + ek + k3 * 2
            x2 = xlist[x * 2 + 2] - ek - k3 * 2
            on = []
            ar = []
            for i in range(0, res):
                a = i * pi / res
                y1 = -cos(a) * k
                if x1 < y1 < x2:
                    myvertex.extend([[y1, fr - 0.005, sin(a) * k + z], [y1, fr + 0.005, sin(a) * k + z]])
                    n = len(myvertex)
                    on.append(n - 1)
                    ar.append(n - 2)
            myvertex.extend(
                [[x1, fr - 0.005, sqrt(k ** 2 - x1 ** 2) + z], [x1, fr + 0.005, sqrt(k ** 2 - x1 ** 2) + z]])
            myvertex.extend([[x1, fr - 0.005, zlist[-3] + ek + k3 * 2], [x1, fr + 0.005, zlist[-3] + ek + k3 * 2]])
            myvertex.extend([[x2, fr - 0.005, zlist[-3] + ek + k3 * 2], [x2, fr + 0.005, zlist[-3] + ek + k3 * 2]])
            myvertex.extend(
                [[x2, fr - 0.005, sqrt(k ** 2 - x2 ** 2) + z], [x2, fr + 0.005, sqrt(k ** 2 - x2 ** 2) + z]])
            n = len(myvertex)
            on.extend([n - 1, n - 3, n - 5, n - 7])
            ar.extend([n - 2, n - 4, n - 6, n - 8])
            myfaces.append(on)
            ar.reverse()
            myfaces.append(ar)
            m = len(myfaces)
            cam.extend([m - 1, m - 2])

    elif op.UST == '3':  # Egri
        if op.DT3 == '1':
            h1 = (op.VL1 / 200) / u
        elif op.DT3 == '2':
            h1 = op.VL3 / 100
        elif op.DT3 == '3':
            h1 = sin(op.VL4 * pi / 180) / cos(op.VL4 * pi / 180)
        z = sqrt(k1 ** 2 + (k1 * h1) ** 2)
        k = sqrt(k2 ** 2 + (k2 * h1) ** 2)
        f = sqrt(k3 ** 2 + (k3 * h1) ** 2) * 2
        myvertex[ust[0]][2] = zlist[-1] + myvertex[ust[0]][0] * h1
        myvertex[ust[1]][2] = zlist[-1] + myvertex[ust[1]][0] * h1
        for i in alt:
            myvertex[i][2] = zlist[-1] + myvertex[i][0] * h1 - z
        myvertex[son[0]][2] = zlist[-1] + myvertex[son[0]][0] * h1
        myvertex[son[1]][2] = zlist[-1] + myvertex[son[1]][0] * h1
        myfaces.append([ust[1], ust[0], son[0], son[1]])
        for i in range(0, mx * 4, 4):
            myfaces.append([alt[i], alt[i + 1], alt[i + 3], alt[i + 2]])
        on = [ust[0]]
        ar = [ust[1]]
        for i in range(0, len(alt) - 1, 2):
            on.append(alt[i])
            ar.append(alt[i + 1])
        on.append(son[0])
        myfaces.append(on)
        ar.append(son[1])
        ar.reverse()
        myfaces.append(ar)
        y = my - 1
        for x in range(0, mx):
            if kx[x][y] is True:
                kapak(myvertex, myfaces, xlist, zlist, x * 2 + 1, y * 2 + 1, k2 / 2, (k1 + k2) * 0.5 - 0.01)
                n = len(myvertex)
                myvertex[n - 5][2] = zlist[-1] + myvertex[n - 5][0] * h1 - z
                myvertex[n - 6][2] = zlist[-1] + myvertex[n - 6][0] * h1 - z - k
                myvertex[n - 7][2] = zlist[-1] + myvertex[n - 7][0] * h1 - z - k
                myvertex[n - 8][2] = zlist[-1] + myvertex[n - 8][0] * h1 - z
                myvertex[n - 9][2] = zlist[-1] + myvertex[n - 9][0] * h1 - z
                myvertex[n - 10][2] = zlist[-1] + myvertex[n - 10][0] * h1 - z - k
                myvertex[n - 11][2] = zlist[-1] + myvertex[n - 11][0] * h1 - z - k
                myvertex[n - 12][2] = zlist[-1] + myvertex[n - 12][0] * h1 - z
                fitil(myvertex, myfaces, xlist, zlist, x * 2 + 1, y * 2 + 1, k3, (k1 + k2) * 0.5 - 0.01, k2)
                n = len(myvertex)
                myvertex[n - 2][2] = zlist[-1] + myvertex[n - 2][0] * h1 - z - k - f
                myvertex[n - 3][2] = zlist[-1] + myvertex[n - 3][0] * h1 - z - k - f
                myvertex[n - 6][2] = zlist[-1] + myvertex[n - 6][0] * h1 - z - k - f
                myvertex[n - 7][2] = zlist[-1] + myvertex[n - 7][0] * h1 - z - k - f
                myvertex[n - 13][2] = zlist[-1] + myvertex[n - 13][0] * h1 - z - k
                myvertex[n - 14][2] = zlist[-1] + myvertex[n - 14][0] * h1 - z - k - f
                myvertex[n - 15][2] = zlist[-1] + myvertex[n - 15][0] * h1 - z - k - f
                myvertex[n - 16][2] = zlist[-1] + myvertex[n - 16][0] * h1 - z - k
                myvertex[n - 17][2] = zlist[-1] + myvertex[n - 17][0] * h1 - z - k
                myvertex[n - 18][2] = zlist[-1] + myvertex[n - 18][0] * h1 - z - k - f
                myvertex[n - 19][2] = zlist[-1] + myvertex[n - 19][0] * h1 - z - k - f
                myvertex[n - 20][2] = zlist[-1] + myvertex[n - 20][0] * h1 - z - k
            else:
                fitil(myvertex, myfaces, xlist, zlist, x * 2 + 1, y * 2 + 1, k3, 0, 0)
                n = len(myvertex)
                myvertex[n - 2][2] = zlist[-1] + myvertex[n - 2][0] * h1 - z - f
                myvertex[n - 3][2] = zlist[-1] + myvertex[n - 3][0] * h1 - z - f
                myvertex[n - 6][2] = zlist[-1] + myvertex[n - 6][0] * h1 - z - f
                myvertex[n - 7][2] = zlist[-1] + myvertex[n - 7][0] * h1 - z - f
                myvertex[n - 13][2] = zlist[-1] + myvertex[n - 13][0] * h1 - z
                myvertex[n - 14][2] = zlist[-1] + myvertex[n - 14][0] * h1 - z - f
                myvertex[n - 15][2] = zlist[-1] + myvertex[n - 15][0] * h1 - z - f
                myvertex[n - 16][2] = zlist[-1] + myvertex[n - 16][0] * h1 - z
                myvertex[n - 17][2] = zlist[-1] + myvertex[n - 17][0] * h1 - z
                myvertex[n - 18][2] = zlist[-1] + myvertex[n - 18][0] * h1 - z - f
                myvertex[n - 19][2] = zlist[-1] + myvertex[n - 19][0] * h1 - z - f
                myvertex[n - 20][2] = zlist[-1] + myvertex[n - 20][0] * h1 - z
            m = len(myfaces)
            cam.extend([m - 1, m - 2])
            ftl.extend([m - 3, m - 4, m - 5, m - 6, m - 7, m - 8, m - 9, m - 10, m - 11, m - 12, m - 13, m - 14])
    elif op.UST == '4':  # Ucgen
        if op.DT3 == '1':
            h1 = (op.VL1 / 100) / u
        elif op.DT3 == '2':
            h1 = op.VL3 / 100
        elif op.DT3 == '3':
            h1 = sin(op.VL4 * pi / 180) / cos(op.VL4 * pi / 180)
        z = sqrt(k1 ** 2 + (k1 * h1) ** 2)
        k = sqrt(k2 ** 2 + (k2 * h1) ** 2)
        f = sqrt(k3 ** 2 + (k3 * h1) ** 2) * 2
        myvertex[ust[0]][2] = zlist[-1] + myvertex[ust[0]][0] * h1
        myvertex[ust[1]][2] = zlist[-1] + myvertex[ust[1]][0] * h1
        for i in alt:
            myvertex[i][2] = zlist[-1] - abs(myvertex[i][0]) * h1 - z
        myvertex[son[0]][2] = zlist[-1] - myvertex[son[0]][0] * h1
        myvertex[son[1]][2] = zlist[-1] - myvertex[son[1]][0] * h1
        myvertex.extend([[0, -k1 / 2, zlist[-1]], [0, k1 / 2, zlist[-1]]])

        x = 0
        for j in range(2, len(alt) - 2, 4):
            if myvertex[alt[j]][0] < 0 < myvertex[alt[j + 2]][0]:
                x = 1

        n = len(myvertex)
        myfaces.extend([[ust[1], ust[0], n - 2, n - 1], [n - 1, n - 2, son[0], son[1]]])
        on = [son[0], n - 2, ust[0]]
        ar = [son[1], n - 1, ust[1]]

        if x == 0:
            myvertex.extend([[0, -k1 / 2, zlist[-1] - z], [0, k1 / 2, zlist[-1] - z]])
        for j in range(0, len(alt) - 2, 4):
            if myvertex[alt[j]][0] < 0 and myvertex[alt[j + 2]][0] < 0:
                myfaces.append([alt[j], alt[j + 1], alt[j + 3], alt[j + 2]])
                on.extend([alt[j], alt[j + 2]])
                ar.extend([alt[j + 1], alt[j + 3]])
            elif myvertex[alt[j]][0] > 0 and myvertex[alt[j + 2]][0] > 0:
                myfaces.append([alt[j], alt[j + 1], alt[j + 3], alt[j + 2]])
                on.extend([alt[j], alt[j + 2]])
                ar.extend([alt[j + 1], alt[j + 3]])
            else:
                n = len(myvertex)
                myfaces.extend([[alt[j], alt[j + 1], n - 1, n - 2], [n - 2, n - 1, alt[j + 3], alt[j + 2]]])
                on.extend([alt[j + 0], n - 2, alt[j + 2]])
                ar.extend([alt[j + 1], n - 1, alt[j + 3]])
        myfaces.append(on)
        ar.reverse()
        myfaces.append(ar)
        y = my - 1
        for x in range(0, mx):
            if myvertex[alt[x * 4]][0] < 0 and myvertex[alt[x * 4 + 2]][0] < 0:
                if kx[x][y] is True:
                    kapak(myvertex, myfaces, xlist, zlist, x * 2 + 1, y * 2 + 1, k2 / 2, (k1 + k2) * 0.5 - 0.01)
                    n = len(myvertex)
                    myvertex[n - 5][2] = zlist[-1] + myvertex[n - 5][0] * h1 - z
                    myvertex[n - 6][2] = zlist[-1] + myvertex[n - 6][0] * h1 - z - k
                    myvertex[n - 7][2] = zlist[-1] + myvertex[n - 7][0] * h1 - z - k
                    myvertex[n - 8][2] = zlist[-1] + myvertex[n - 8][0] * h1 - z
                    myvertex[n - 9][2] = zlist[-1] + myvertex[n - 9][0] * h1 - z
                    myvertex[n - 10][2] = zlist[-1] + myvertex[n - 10][0] * h1 - z - k
                    myvertex[n - 11][2] = zlist[-1] + myvertex[n - 11][0] * h1 - z - k
                    myvertex[n - 12][2] = zlist[-1] + myvertex[n - 12][0] * h1 - z
                    fitil(myvertex, myfaces, xlist, zlist, x * 2 + 1, y * 2 + 1, k3, (k1 + k2) * 0.5 - 0.01, k2)
                    n = len(myvertex)
                    myvertex[n - 2][2] = zlist[-1] + myvertex[n - 2][0] * h1 - z - k - f
                    myvertex[n - 3][2] = zlist[-1] + myvertex[n - 3][0] * h1 - z - k - f
                    myvertex[n - 6][2] = zlist[-1] + myvertex[n - 6][0] * h1 - z - k - f
                    myvertex[n - 7][2] = zlist[-1] + myvertex[n - 7][0] * h1 - z - k - f
                    myvertex[n - 13][2] = zlist[-1] + myvertex[n - 13][0] * h1 - z - k
                    myvertex[n - 14][2] = zlist[-1] + myvertex[n - 14][0] * h1 - z - k - f
                    myvertex[n - 15][2] = zlist[-1] + myvertex[n - 15][0] * h1 - z - k - f
                    myvertex[n - 16][2] = zlist[-1] + myvertex[n - 16][0] * h1 - z - k
                    myvertex[n - 17][2] = zlist[-1] + myvertex[n - 17][0] * h1 - z - k
                    myvertex[n - 18][2] = zlist[-1] + myvertex[n - 18][0] * h1 - z - k - f
                    myvertex[n - 19][2] = zlist[-1] + myvertex[n - 19][0] * h1 - z - k - f
                    myvertex[n - 20][2] = zlist[-1] + myvertex[n - 20][0] * h1 - z - k
                else:
                    fitil(myvertex, myfaces, xlist, zlist, x * 2 + 1, y * 2 + 1, k3, 0, 0)
                    n = len(myvertex)
                    myvertex[n - 2][2] = zlist[-1] + myvertex[n - 2][0] * h1 - z - f
                    myvertex[n - 3][2] = zlist[-1] + myvertex[n - 3][0] * h1 - z - f
                    myvertex[n - 6][2] = zlist[-1] + myvertex[n - 6][0] * h1 - z - f
                    myvertex[n - 7][2] = zlist[-1] + myvertex[n - 7][0] * h1 - z - f
                    myvertex[n - 13][2] = zlist[-1] + myvertex[n - 13][0] * h1 - z
                    myvertex[n - 14][2] = zlist[-1] + myvertex[n - 14][0] * h1 - z - f
                    myvertex[n - 15][2] = zlist[-1] + myvertex[n - 15][0] * h1 - z - f
                    myvertex[n - 16][2] = zlist[-1] + myvertex[n - 16][0] * h1 - z
                    myvertex[n - 17][2] = zlist[-1] + myvertex[n - 17][0] * h1 - z
                    myvertex[n - 18][2] = zlist[-1] + myvertex[n - 18][0] * h1 - z - f
                    myvertex[n - 19][2] = zlist[-1] + myvertex[n - 19][0] * h1 - z - f
                    myvertex[n - 20][2] = zlist[-1] + myvertex[n - 20][0] * h1 - z
                m = len(myfaces)
                cam.extend([m - 1, m - 2])
                ftl.extend([m - 3, m - 4, m - 5, m - 6, m - 7, m - 8, m - 9, m - 10, m - 11, m - 12, m - 13, m - 14])
            elif myvertex[alt[x * 4]][0] > 0 and myvertex[alt[x * 4 + 2]][0] > 0:
                if kx[x][y] is True:
                    kapak(myvertex, myfaces, xlist, zlist, x * 2 + 1, y * 2 + 1, k2 / 2, (k1 + k2) * 0.5 - 0.01)
                    n = len(myvertex)
                    myvertex[n - 5][2] = zlist[-1] - myvertex[n - 5][0] * h1 - z
                    myvertex[n - 6][2] = zlist[-1] - myvertex[n - 6][0] * h1 - z - k
                    myvertex[n - 7][2] = zlist[-1] - myvertex[n - 7][0] * h1 - z - k
                    myvertex[n - 8][2] = zlist[-1] - myvertex[n - 8][0] * h1 - z
                    myvertex[n - 9][2] = zlist[-1] - myvertex[n - 9][0] * h1 - z
                    myvertex[n - 10][2] = zlist[-1] - myvertex[n - 10][0] * h1 - z - k
                    myvertex[n - 11][2] = zlist[-1] - myvertex[n - 11][0] * h1 - z - k
                    myvertex[n - 12][2] = zlist[-1] - myvertex[n - 12][0] * h1 - z
                    fitil(myvertex, myfaces, xlist, zlist, x * 2 + 1, y * 2 + 1, k3, (k1 + k2) * 0.5 - 0.01, k2)
                    n = len(myvertex)
                    myvertex[n - 2][2] = zlist[-1] - myvertex[n - 2][0] * h1 - z - k - f
                    myvertex[n - 3][2] = zlist[-1] - myvertex[n - 3][0] * h1 - z - k - f
                    myvertex[n - 6][2] = zlist[-1] - myvertex[n - 6][0] * h1 - z - k - f
                    myvertex[n - 7][2] = zlist[-1] - myvertex[n - 7][0] * h1 - z - k - f
                    myvertex[n - 13][2] = zlist[-1] - myvertex[n - 13][0] * h1 - z - k
                    myvertex[n - 14][2] = zlist[-1] - myvertex[n - 14][0] * h1 - z - k - f
                    myvertex[n - 15][2] = zlist[-1] - myvertex[n - 15][0] * h1 - z - k - f
                    myvertex[n - 16][2] = zlist[-1] - myvertex[n - 16][0] * h1 - z - k
                    myvertex[n - 17][2] = zlist[-1] - myvertex[n - 17][0] * h1 - z - k
                    myvertex[n - 18][2] = zlist[-1] - myvertex[n - 18][0] * h1 - z - k - f
                    myvertex[n - 19][2] = zlist[-1] - myvertex[n - 19][0] * h1 - z - k - f
                    myvertex[n - 20][2] = zlist[-1] - myvertex[n - 20][0] * h1 - z - k
                else:
                    fitil(myvertex, myfaces, xlist, zlist, x * 2 + 1, y * 2 + 1, k3, 0, 0)
                    n = len(myvertex)
                    myvertex[n - 2][2] = zlist[-1] - myvertex[n - 2][0] * h1 - z - f
                    myvertex[n - 3][2] = zlist[-1] - myvertex[n - 3][0] * h1 - z - f
                    myvertex[n - 6][2] = zlist[-1] - myvertex[n - 6][0] * h1 - z - f
                    myvertex[n - 7][2] = zlist[-1] - myvertex[n - 7][0] * h1 - z - f
                    myvertex[n - 13][2] = zlist[-1] - myvertex[n - 13][0] * h1 - z
                    myvertex[n - 14][2] = zlist[-1] - myvertex[n - 14][0] * h1 - z - f
                    myvertex[n - 15][2] = zlist[-1] - myvertex[n - 15][0] * h1 - z - f
                    myvertex[n - 16][2] = zlist[-1] - myvertex[n - 16][0] * h1 - z
                    myvertex[n - 17][2] = zlist[-1] - myvertex[n - 17][0] * h1 - z
                    myvertex[n - 18][2] = zlist[-1] - myvertex[n - 18][0] * h1 - z - f
                    myvertex[n - 19][2] = zlist[-1] - myvertex[n - 19][0] * h1 - z - f
                    myvertex[n - 20][2] = zlist[-1] - myvertex[n - 20][0] * h1 - z
                m = len(myfaces)
                cam.extend([m - 1, m - 2])
                ftl.extend([m - 3, m - 4, m - 5, m - 6, m - 7, m - 8, m - 9, m - 10, m - 11, m - 12, m - 13, m - 14])
            else:
                k4 = k3 * 2
                if kx[x][y] is True:
                    zz = (k1 + k2) * 0.5 - 0.01
                    xx = xlist[x * 2 + 1]
                    myvertex.extend([[xx, -k2 / 2 + zz, zlist[-3]], [xx + k2, -k2 / 2 + zz, zlist[-3] + k2],
                                     [xx + k2, k2 / 2 + zz, zlist[-3] + k2], [xx, k2 / 2 + zz, zlist[-3]]])
                    myvertex.extend(
                        [[xx, -k2 / 2 + zz, zlist[-1] + xx * h1 - z], [xx + k2, -k2 / 2 + zz,
                                                                       zlist[-1] + (xx + k2) * h1 - z - k],
                         [xx + k2, k2 / 2 + zz, zlist[-1] + (xx + k2) * h1 - z - k],
                         [xx, k2 / 2 + zz, zlist[-1] + xx * h1 - z]])
                    myvertex.extend([[0, -k2 / 2 + zz, zlist[-1] - z], [0, -k2 / 2 + zz, zlist[-1] - z - k],
                                     [0, k2 / 2 + zz, zlist[-1] - z - k], [0, k2 / 2 + zz, zlist[-1] - z]])
                    xx = xlist[x * 2 + 2]
                    myvertex.extend(
                        [[xx, -k2 / 2 + zz, zlist[-1] - xx * h1 - z], [xx - k2, -k2 / 2 + zz,
                                                                       zlist[-1] - (xx - k2) * h1 - z - k],
                         [xx - k2, k2 / 2 + zz, zlist[-1] - (xx - k2) * h1 - z - k],
                         [xx, k2 / 2 + zz, zlist[-1] - xx * h1 - z]])
                    myvertex.extend([[xx, -k2 / 2 + zz, zlist[-3]], [xx - k2, -k2 / 2 + zz, zlist[-3] + k2],
                                     [xx - k2, k2 / 2 + zz, zlist[-3] + k2], [xx, k2 / 2 + zz, zlist[-3]]])
                    n = len(myvertex)
                    myfaces.extend([[n - 20, n - 19, n - 15, n - 16], [n - 19, n - 18, n - 14, n - 15],
                                    [n - 18, n - 17, n - 13, n - 14], [n - 17, n - 20, n - 16, n - 13]])
                    myfaces.extend([[n - 16, n - 15, n - 11, n - 12], [n - 15, n - 14, n - 10, n - 11],
                                    [n - 14, n - 13, n - 9, n - 10], [n - 13, n - 16, n - 12, n - 9]])
                    myfaces.extend(
                        [[n - 12, n - 11, n - 7, n - 8], [n - 11, n - 10, n - 6, n - 7], [n - 10, n - 9, n - 5, n - 6],
                         [n - 9, n - 12, n - 8, n - 5]])
                    myfaces.extend(
                        [[n - 8, n - 7, n - 3, n - 4], [n - 7, n - 6, n - 2, n - 3], [n - 6, n - 5, n - 1, n - 2],
                         [n - 5, n - 8, n - 4, n - 1]])
                    myfaces.extend(
                        [[n - 4, n - 3, n - 19, n - 20], [n - 3, n - 2, n - 18, n - 19], [n - 2, n - 1, n - 17, n - 18],
                         [n - 1, n - 4, n - 20, n - 17]])
                    xx = xlist[x * 2 + 1]
                    myvertex.extend([[xx + k2, -k3 + zz, zlist[-3] + k2], [xx + k4 + k2, -k3 + zz, zlist[-3] + k2 + k4],
                                     [xx + k4 + k2, k3 + zz, zlist[-3] + k2 + k4], [xx + k2, k3 + zz, zlist[-3] + k2]])
                    myvertex.extend([[xx + k2, -k3 + zz, zlist[-1] + (xx + k2) * h1 - z - k],
                                     [xx + k4 + k2, -k3 + zz, zlist[-1] + (xx + k2 + k4) * h1 - z - k - f],
                                     [xx + k4 + k2, k3 + zz, zlist[-1] + (xx + k2 + k4) * h1 - z - k - f],
                                     [xx + k2, k3 + zz, zlist[-1] + (xx + k2) * h1 - z - k]])
                    myvertex.extend([[0, -k3 + zz, zlist[-1] - k - z], [0, -k3 + zz, zlist[-1] - k - z - f],
                                     [0, k3 + zz, zlist[-1] - k - z - f], [0, k3 + zz, zlist[-1] - k - z]])
                    xx = xlist[x * 2 + 2]
                    myvertex.extend([[xx - k2, -k3 + zz, zlist[-1] - (xx - k2) * h1 - z - k],
                                     [xx - k4 - k2, -k3 + zz, zlist[-1] - (xx - k2 - k4) * h1 - z - k - f],
                                     [xx - k4 - k2, k3 + zz, zlist[-1] - (xx - k2 - k4) * h1 - z - k - f],
                                     [xx - k2, k3 + zz, zlist[-1] - (xx - k2) * h1 - z - k]])
                    myvertex.extend([[xx - k2, -k3 + zz, zlist[-3] + k2], [xx - k4 - k2, -k3 + zz, zlist[-3] + k2 + k4],
                                     [xx - k4 - k2, k3 + zz, zlist[-3] + k2 + k4], [xx - k2, k3 + zz, zlist[-3] + k2]])
                    n = len(myvertex)
                    myfaces.extend([[n - 20, n - 19, n - 15, n - 16], [n - 19, n - 18, n - 14, n - 15],
                                    [n - 18, n - 17, n - 13, n - 14]])
                    myfaces.extend([[n - 16, n - 15, n - 11, n - 12], [n - 15, n - 14, n - 10, n - 11],
                                    [n - 14, n - 13, n - 9, n - 10]])
                    myfaces.extend(
                        [[n - 12, n - 11, n - 7, n - 8], [n - 11, n - 10, n - 6, n - 7], [n - 10, n - 9, n - 5, n - 6]])
                    myfaces.extend(
                        [[n - 8, n - 7, n - 3, n - 4], [n - 7, n - 6, n - 2, n - 3], [n - 6, n - 5, n - 1, n - 2]])
                    myfaces.extend([[n - 4, n - 3, n - 19, n - 20], [n - 3, n - 2, n - 18, n - 19],
                                    [n - 2, n - 1, n - 17, n - 18]])
                    xx = xlist[x * 2 + 1]
                    myvertex.extend(
                        [[xx + k4 + k2, -k3 + zz, zlist[-3] + k2 + k4], [xx + k4 + k2, k3 + zz, zlist[-3] + k2 + k4]])
                    myvertex.extend([[xx + k4 + k2, -k3 + zz, zlist[-1] + (xx + k2 + k4) * h1 - z - k - f],
                                     [xx + k4 + k2, k3 + zz, zlist[-1] + (xx + k2 + k4) * h1 - z - k - f]])
                    myvertex.extend([[0, -k3 + zz, zlist[-1] - k - z - f], [0, k3 + zz, zlist[-1] - k - z - f]])
                    xx = xlist[x * 2 + 2]
                    myvertex.extend([[xx - k4 - k2, -k3 + zz, zlist[-1] - (xx - k2 - k4) * h1 - z - k - f],
                                     [xx - k4 - k2, k3 + zz, zlist[-1] - (xx - k2 - k4) * h1 - z - k - f]])
                    myvertex.extend(
                        [[xx - k4 - k2, -k3 + zz, zlist[-3] + k2 + k4], [xx - k4 - k2, k3 + zz, zlist[-3] + k2 + k4]])
                    myfaces.extend([[n + 8, n + 6, n + 4, n + 2, n + 0], [n + 1, n + 3, n + 5, n + 7, n + 9]])
                else:
                    xx = xlist[x * 2 + 1]
                    myvertex.extend(
                        [[xx, -k3, zlist[-3]], [xx + k4, -k3, zlist[-3] + k4], [xx + k4, k3, zlist[-3] + k4],
                         [xx, k3, zlist[-3]]])
                    myvertex.extend(
                        [[xx, -k3, zlist[-1] + xx * h1 - z], [xx + k4, -k3, zlist[-1] + (xx + k4) * h1 - z - f],
                         [xx + k4, k3, zlist[-1] + (xx + k4) * h1 - z - f], [xx, k3, zlist[-1] + xx * h1 - z]])
                    myvertex.extend(
                        [[0, -k3, zlist[-1] - z], [0, -k3, zlist[-1] - z - f], [0, k3, zlist[-1] - z - f],
                         [0, k3, zlist[-1] - z]])
                    xx = xlist[x * 2 + 2]
                    myvertex.extend(
                        [[xx, -k3, zlist[-1] - xx * h1 - z], [xx - k4, -k3, zlist[-1] - (xx - k4) * h1 - z - f],
                         [xx - k4, k3, zlist[-1] - (xx - k4) * h1 - z - f], [xx, k3, zlist[-1] - xx * h1 - z]])
                    myvertex.extend(
                        [[xx, -k3, zlist[-3]], [xx - k4, -k3, zlist[-3] + k4], [xx - k4, k3, zlist[-3] + k4],
                         [xx, k3, zlist[-3]]])
                    n = len(myvertex)
                    myfaces.extend([[n - 20, n - 19, n - 15, n - 16], [n - 19, n - 18, n - 14, n - 15],
                                    [n - 18, n - 17, n - 13, n - 14]])
                    myfaces.extend([[n - 16, n - 15, n - 11, n - 12], [n - 15, n - 14, n - 10, n - 11],
                                    [n - 14, n - 13, n - 9, n - 10]])
                    myfaces.extend(
                        [[n - 12, n - 11, n - 7, n - 8], [n - 11, n - 10, n - 6, n - 7], [n - 10, n - 9, n - 5, n - 6]])
                    myfaces.extend(
                        [[n - 8, n - 7, n - 3, n - 4], [n - 7, n - 6, n - 2, n - 3], [n - 6, n - 5, n - 1, n - 2]])
                    myfaces.extend([[n - 4, n - 3, n - 19, n - 20], [n - 3, n - 2, n - 18, n - 19],
                                    [n - 2, n - 1, n - 17, n - 18]])
                    xx = xlist[x * 2 + 1]
                    myvertex.extend([[xx + k4, -0.005, zlist[-3] + k4], [xx + k4, 0.005, zlist[-3] + k4]])
                    myvertex.extend([[xx + k4, -0.005, zlist[-1] + (xx + k4) * h1 - z - f],
                                     [xx + k4, 0.005, zlist[-1] + (xx + k4) * h1 - z - f]])
                    myvertex.extend([[0, -0.005, zlist[-1] - z - f], [0, 0.005, zlist[-1] - z - f]])
                    xx = xlist[x * 2 + 2]
                    myvertex.extend([[xx - k4, -0.005, zlist[-1] - (xx - k4) * h1 - z - f],
                                     [xx - k4, 0.005, zlist[-1] - (xx - k4) * h1 - z - f]])
                    myvertex.extend([[xx - k4, -0.005, zlist[-3] + k4], [xx - k4, 0.005, zlist[-3] + k4]])
                    myfaces.extend([[n + 8, n + 6, n + 4, n + 2, n + 0], [n + 1, n + 3, n + 5, n + 7, n + 9]])
                m = len(myfaces)
                cam.extend([m - 1, m - 2])
                ftl.extend(
                    [m - 3, m - 4, m - 5, m - 6, m - 7, m - 8, m - 9, m - 10, m - 11, m - 12, m - 13, m - 14, m - 15,
                     m - 16, m - 17])
    # Mermer
    if op.mr is True:
        mrh = -op.mr1 / 100
        mrg = op.mr2 / 100
        mdv = (op.mr3 / 200) + mrg
        msv = -(mdv + (op.mr4 / 100))
        myvertex.extend([[-u, mdv, 0], [u, mdv, 0], [-u, msv, 0], [u, msv, 0], [-u, mdv, mrh], [u, mdv, mrh],
                         [-u, msv, mrh],
                         [u, msv, mrh]])
        n = len(myvertex)
        myfaces.extend([[n - 1, n - 2, n - 4, n - 3], [n - 3, n - 4, n - 8, n - 7], [n - 6, n - 5, n - 7, n - 8],
                        [n - 2, n - 1, n - 5, n - 6], [n - 4, n - 2, n - 6, n - 8], [n - 5, n - 1, n - 3, n - 7]])
        n = len(myfaces)
        mer.extend([n - 1, n - 2, n - 3, n - 4, n - 5, n - 6])

    return ftl, cam, mer, sm


# ------------------------------------------------------------------
# Define property group class to create or modify
# ------------------------------------------------------------------


class GeneralProperties(bpy.types.PropertyGroup):
    prs = bpy.props.EnumProperty(items=(('1', "WINDOW 250X200", ""),
                                        ('2', "WINDOW 200X200", ""),
                                        ('3', "WINDOW 180X200", ""),
                                        ('4', "WINDOW 180X160", ""),
                                        ('5', "WINDOW 160X160", ""),
                                        ('6', "WINDOW 50X50", ""),
                                        ('7', "DOOR 80X250", ""),
                                        ('8', "DOOR 80X230", "")),
                                 name="",
                                 description='Predefined types',
                                 update=update_using_default)
    son = prs
    gen = bpy.props.IntProperty(name='H Count', min=1, max=8, default=3, description='Horizontal Panes',
                                update=update_window)
    yuk = bpy.props.IntProperty(name='V Count', min=1, max=5, default=1, description='Vertical Panes',
                                update=update_window)
    kl1 = bpy.props.IntProperty(name='Outer Frame', min=2, max=50, default=5, description='Outside Frame Thickness',
                                update=update_window)
    kl2 = bpy.props.IntProperty(name='Risers', min=2, max=50, default=5, description='Risers Width',
                                update=update_window)
    fk = bpy.props.IntProperty(name='Inner Frame', min=1, max=20, default=2, description='Inside Frame Thickness',
                               update=update_window)

    mr = bpy.props.BoolProperty(name='Sill', default=True, description='Window Sill', update=update_window)
    mr1 = bpy.props.IntProperty(name='', min=1, max=20, default=4, description='Height', update=update_window)
    mr2 = bpy.props.IntProperty(name='', min=0, max=20, default=4, description='First Depth', update=update_window)
    mr3 = bpy.props.IntProperty(name='', min=1, max=50, default=20, description='Second Depth', update=update_window)
    mr4 = bpy.props.IntProperty(name='', min=0, max=50, default=0, description='Extrusion for Jamb',
                                update=update_window)

    mt1 = bpy.props.EnumProperty(items=(('1', "PVC", ""), ('2', "WOOD", ""), ('3', "Plastic", "")), name="",
                                 default='1',
                                 description='Material to use',
                                 update=update_window)
    mt2 = bpy.props.EnumProperty(items=(('1', "PVC", ""), ('2', "WOOD", ""), ('3', "Plastic", "")), name="",
                                 default='3',
                                 description='Material to use',
                                 update=update_window)

    UST = bpy.props.EnumProperty(
        items=(('1', "Flat", ""), ('2', "Arch", ""), ('3', "Inclined", ""), ('4', "Triangle", "")),
        name="Top", default='1',
        description='Type of window upper section',
        update=update_window)
    DT2 = bpy.props.EnumProperty(items=(('1', "Difference", ""), ('2', "Radius", "")), name="", default='1',
                                 update=update_window)
    DT3 = bpy.props.EnumProperty(items=(('1', "Difference", ""), ('2', "Incline %", ""), ('3', "Incline Angle", "")),
                                 name="",
                                 default='1', update=update_window)

    VL1 = bpy.props.IntProperty(name='', min=-10000, max=10000, default=30, update=update_window)  # Fark
    VL2 = bpy.props.IntProperty(name='', min=1, max=10000, default=30, update=update_window)  # Cap
    VL3 = bpy.props.IntProperty(name='', min=-100, max=100, default=30, update=update_window)  # Egim %
    VL4 = bpy.props.IntProperty(name='', min=-45, max=45, default=30, update=update_window)  # Egim Aci

    res = bpy.props.IntProperty(name='Resolution', min=2, max=360, default=36, update=update_window)  # Res

    gnx0 = bpy.props.IntProperty(name='', min=1, max=300, default=60, description='1st Window Width',
                                 update=update_window)
    gnx1 = bpy.props.IntProperty(name='', min=1, max=300, default=110, description='2nd Window Width',
                                 update=update_window)
    gnx2 = bpy.props.IntProperty(name='', min=1, max=300, default=60, description='3rd Window Width',
                                 update=update_window)
    gnx3 = bpy.props.IntProperty(name='', min=1, max=300, default=60, description='4th Window Width',
                                 update=update_window)
    gnx4 = bpy.props.IntProperty(name='', min=1, max=300, default=60, description='5th Window Width',
                                 update=update_window)
    gnx5 = bpy.props.IntProperty(name='', min=1, max=300, default=60, description='6th Window Width',
                                 update=update_window)
    gnx6 = bpy.props.IntProperty(name='', min=1, max=300, default=60, description='7th Window Width',
                                 update=update_window)
    gnx7 = bpy.props.IntProperty(name='', min=1, max=300, default=60, description='8th Window Width',
                                 update=update_window)

    gny0 = bpy.props.IntProperty(name='', min=1, max=300, default=190, description='1st Row Height',
                                 update=update_window)
    gny1 = bpy.props.IntProperty(name='', min=1, max=300, default=45, description='2nd Row Height',
                                 update=update_window)
    gny2 = bpy.props.IntProperty(name='', min=1, max=300, default=45, description='3rd Row Height',
                                 update=update_window)
    gny3 = bpy.props.IntProperty(name='', min=1, max=300, default=45, description='4th Row Height',
                                 update=update_window)
    gny4 = bpy.props.IntProperty(name='', min=1, max=300, default=45, description='5th Row Height',
                                 update=update_window)

    k00 = bpy.props.BoolProperty(name='', default=True, update=update_window)
    k01 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k02 = bpy.props.BoolProperty(name='', default=True, update=update_window)
    k03 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k04 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k05 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k06 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k07 = bpy.props.BoolProperty(name='', default=False, update=update_window)

    k10 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k11 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k12 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k13 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k14 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k15 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k16 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k17 = bpy.props.BoolProperty(name='', default=False, update=update_window)

    k20 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k21 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k22 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k23 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k24 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k25 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k26 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k27 = bpy.props.BoolProperty(name='', default=False, update=update_window)

    k30 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k31 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k32 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k33 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k34 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k35 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k36 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k37 = bpy.props.BoolProperty(name='', default=False, update=update_window)

    k40 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k41 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k42 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k43 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k44 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k45 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k46 = bpy.props.BoolProperty(name='', default=False, update=update_window)
    k47 = bpy.props.BoolProperty(name='', default=False, update=update_window)


bpy.utils.register_class(GeneralProperties)
bpy.types.Object.WindowGenerator = bpy.props.CollectionProperty(type=GeneralProperties)
# ------------------------------------------------------------------
# Define panel class to modify myobjects.
# ------------------------------------------------------------------


class WindowEditPanel(bpy.types.Panel):
    bl_idname = "window.edit_panel"
    bl_label = "Window Properties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Window'
    # -----------------------------------------------------
    # Draw (create UI interface)
    # -----------------------------------------------------

    def draw(self, context):
        o = context.object
        # If the selected object didn't be created with the group 'WindowGenerator', this panel is not created.
        # noinspection PyBroadException
        try:
            if 'WindowGenerator' not in o:
                return
        except:
            return

        layout = self.layout
        if bpy.context.mode == 'EDIT_MESH':
            layout.label('Warning: Operator does not work in edit mode.', icon='ERROR')
        else:
            myobject = o.WindowGenerator[0]
            layout.prop(myobject, 'prs')
            box = layout.box()
            box.prop(myobject, 'gen')
            box.prop(myobject, 'yuk')
            box.prop(myobject, 'kl1')
            box.prop(myobject, 'kl2')
            box.prop(myobject, 'fk')

            box.prop(myobject, 'mr')
            if myobject.mr is True:
                row = box.row()
                row.prop(myobject, 'mr1')
                row.prop(myobject, 'mr2')
                row = box.row()
                row.prop(myobject, 'mr3')
                row.prop(myobject, 'mr4')
            row = layout.row()
            row.label('Frame')
            row.label('Inner Frame')
            row = layout.row()
            row.prop(myobject, 'mt1')
            row.prop(myobject, 'mt2')

            box.prop(myobject, 'UST')
            if myobject.UST == '2':
                row = box.row()
                row.prop(myobject, 'DT2')
                if myobject.DT2 == '1':
                    row.prop(myobject, 'VL1')
                elif myobject.DT2 == '2':
                    row.prop(myobject, 'VL2')
                box.prop(myobject, 'res')
            elif myobject.UST == '3':
                row = box.row()
                row.prop(myobject, 'DT3')
                if myobject.DT3 == '1':
                    row.prop(myobject, 'VL1')
                elif myobject.DT3 == '2':
                    row.prop(myobject, 'VL3')
                elif myobject.DT3 == '3':
                    row.prop(myobject, 'VL4')
            elif myobject.UST == '4':
                row = box.row()
                row.prop(myobject, 'DT3')
                if myobject.DT3 == '1':
                    row.prop(myobject, 'VL1')
                elif myobject.DT3 == '2':
                    row.prop(myobject, 'VL3')
                elif myobject.DT3 == '3':
                    row.prop(myobject, 'VL4')
            row = layout.row()
            for i in range(0, myobject.gen):
                row.prop(myobject, 'gnx' + str(i))
            for j in range(0, myobject.yuk):
                row = layout.row()
                row.prop(myobject, 'gny' + str(myobject.yuk - j - 1))
                for i in range(0, myobject.gen):
                    row.prop(myobject, 'k' + str(myobject.yuk - j - 1) + str(i))