import bpy


#create the barndoors objects
class AddBarndoors(bpy.types.Operator):

    def create_mesh(name):
        me = bpy.data.meshes.new(name)
        ob = bpy.data.objects.new(name, me)

        bpy.data.scenes[0].objects.link(ob)

        me.from_pydata([(-1.0, -1.0, 0.0), (1.0, -1.0, 0.0), (-1.0, 1.0, 0.0),
                        (1.0, 1.0, 0.0), (-3.17727, 3.17981, 0.0),
                        (-4.49474, 0.00163, 0.0), (-3.17925, -3.1775, 0.0),
                        (-0.0014, -4.4953, 0.0), (3.17727, -3.17981, 0.0),
                        (4.49474, -0.00163, 0.0), (3.17925, 3.1775, 0.06124),
                        (0.0014, 4.4953, 0.01438), (0.0, -1.0, 0.0),
                        (1.0, 0.0, 0.0), (-1.0, 0.0, 0.0), (0.0, 1.0, 0.0)],
                       [(12, 0), (13, 1), (14, 3), (15, 2), (5, 4), (6, 5),
                        (7, 6), (8, 7), (9, 8), (10, 9), (11, 10), (4, 11),
                        (12, 2), (13, 0), (14, 1), (15, 3), (2, 4), (11, 15),
                        (3, 10), (14, 9), (5, 12), (0, 6), (7, 13), (1, 8)],
                       [(14, 9, 10, 3), (10, 11, 15, 3), (15, 11, 4, 2),
                        (4, 5, 12, 2), (12, 5, 6, 0), (6, 7, 13, 0),
                        (13, 7, 8, 1), (8, 9, 14, 1)])
        me.update()

        return me

    create_mesh("Barndoors")
#    bpy.context.object.parent = bpy.data.objects["Spot"]


class ObjectsCreationControls(bpy.types.PropertyGroup):

    from bpy.props import FloatProperty

    RightPanel = FloatProperty(
        attr="",
        name="",
        description="Angle of the right panel",
        unit="ROTATION",
        soft_min=-3.14159265, soft_max=3.14159265, step=10.00, default=0.00)
