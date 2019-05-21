import bpy
from . init_base_material import create_base_mat
from .. import M3utils as m3


class AssignUniqueMaterials(bpy.types.Operator):
    bl_idname = "machin3.assign_unique_materials"
    bl_label = "MACHIN3: Assign Unique Materials"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selection = m3.selected_objects()
        m3.unselect_all("OBJECT")

        for obj in selection:
            if obj.type == "MESH":
                m3.make_active(obj)
                obj.select = True

                # skip decals:
                mat = obj.material_slots[0].material
                if mat:
                    if any([x in mat.name for x in ["decal01", "decal02", "paneling01", "info01", "decals"]]):
                        print("Skipping '%s', is decal." % (obj.name))
                        continue

                print("Applying unique materials based on edge seams to object: '%s'" % (obj.name))

                # unhide and desellect everything
                m3.set_mode("EDIT")
                m3.set_mode("FACE")
                m3.unhide_all("MESH")
                m3.unselect_all("MESH")
                m3.set_mode("OBJECT")

                mesh = obj.data
                keepgoing = True
                foundidx = 0
                while keepgoing:
                    foundunassigned = False
                    for face in mesh.polygons:
                        if face.hide is False:
                            # print("Face '%d' represents a unique material" % (face.index))
                            face.select = True
                            foundunassigned = True
                            break

                    if foundunassigned:
                        # get or create unique material
                        if foundidx == 0:
                            matname = "base"
                        else:
                            matname = "base." + str(foundidx).zfill(3)

                        mat = bpy.data.materials.get(matname)

                        if not mat:
                            mat = create_base_mat(matname)

                        # append material if necessary and get the slot idx
                        if mat.name not in obj.data.materials:
                            obj.data.materials.append(mat)

                        for idx, slot in enumerate(obj.material_slots):
                                if slot.material == mat:
                                    obj.active_material_index = idx
                                    break

                        m3.set_mode("EDIT")
                        bpy.ops.mesh.select_linked(delimit={'SEAM'})
                        bpy.ops.object.material_slot_assign()
                        print(" » Assigned material '%s'" % (mat.name))
                        bpy.ops.mesh.hide(unselected=False)
                        m3.set_mode("OBJECT")

                        foundidx += 1
                    else:
                        keepgoing = False
                        m3.set_mode("EDIT")
                        m3.unhide_all("MESH")
                        m3.set_mode("OBJECT")

        # reset selection
        for obj in selection:
            obj.select = True

        return {'FINISHED'}
