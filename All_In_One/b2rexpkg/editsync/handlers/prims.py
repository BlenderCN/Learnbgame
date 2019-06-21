"""
 MapModule: Provides map functionality, with information from coarse updates.
"""
from .base import SyncModule

from b2rexpkg.tools.primmesher import PrimMesh
from b2rexpkg.tools.primmesher import Extrusion, PathType, ProfileShape, HollowShape

from .props.prims import B2RexPrimProps

import bpy

class PrimsModule(SyncModule):
    def register(self, parent):
        """
        Register this module with the editor
        """
        self.register_property(bpy.types.B2RexMeshProps, 'prim', B2RexPrimProps)

        parent.registerCommand('CoarseLocationUpdate', self.processCoarseLocationUpdate)

    def unregister(self, parent):
        """
        Unregister this module from the editor
        """
        self.unregister_property(bpy.types.B2RexMeshProps, 'prim')
        parent.unregisterCommand('CoarseLocationUpdate')

    def create(self, objId, pars):
        editor = self._parent
        if 'Name' in pars:
            name = pars['Name']
        else:
            name = 'prim'
        mesh = bpy.data.meshes.new(name)
        sides = 5
        hollowSides = 5

        profileCurve = pars['ProfileCurve']
        profileShape = profileCurve & 0x0f
        hollowShape = profileCurve & 0xf0

        if profileShape == ProfileShape.Circle:
            sides = 10
        elif profileShape == ProfileShape.Square:
            sides = 4
        elif profileShape == ProfileShape.IsometricTriangle:
            sides = 3
        elif profileShape == ProfileShape.EquilateralTriangle:
            sides = 3
        elif profileShape == ProfileShape.RightTriangle:
            sides = 3
        elif profileShape == ProfileShape.HalfCircle:
            sides = 10

        if hollowShape == HollowShape.Same:
            hollowSides = sides
        elif hollowShape == HollowShape.Circle:
            hollowSides = 10
        elif hollowShape == HollowShape.Square:
            hollowSides = 4
        elif hollowShape == HollowShape.Triangle:
            hollowSides = 3


        profileStart = pars['ProfileBegin']
        profileEnd = pars['ProfileEnd']
        hollow = pars['ProfileHollow']

        p = PrimMesh(sides, profileStart, profileEnd, hollow, hollowSides)
        if profileShape in [ProfileShape.RightTriangle, ProfileShape.HalfCircle]:
            p._pathCutBegin = 0.0
            p._pathCutEnd = 0.5
        else:
            p._pathCutBegin = pars['PathBegin']
            p._pathCutEnd = pars['PathEnd']
        p._twistBegin = pars['PathTwistBegin']
        p._twistEnd = pars['PathTwist']
        p._topShearX = pars['PathShearX']
        p._topShearY = pars['PathShearY']
        p._holeSizeX = pars['PathScaleX']
        p._holeSizeY = pars['PathScaleY']
        p._radius = pars['PathRadiusOffset']
        p._taperX = pars['PathTaperX']
        p._taperY = pars['PathTaperY']
        p._revolutions = pars['PathRevolutions']
        p._skew = pars['PathSkew']
        p._viewerMode = True

        if pars['PathCurve'] == Extrusion.Straight:
            p.Extrude(PathType.Linear)
        elif pars['PathCurve'] in [Extrusion.Curve1, Extrusion.Curve2]:
            p.Extrude(PathType.Circular)
        elif pars['PathCurve'] == Extrusion.Flexible:
            p.Extrude(PathType.Flexible)
        else:
            print("Unknown Path Type!!", pars['PathCurve'])
            return

        mesh = self.apply_prim(p)

        obj = editor.Object.createObjectWithMesh(mesh, objId, objId)

        return obj

    def generate(self, context):
        obj = self._parent.getSelected()[0]
        props = obj.data.opensim.prim
        sides = props.sides
        profileStart = props.profile[0]
        profileEnd = props.profile[1]
        hollow = props.hollow
        hollowSides = props.hollowSides

        p = PrimMesh(sides, profileStart, profileEnd, hollow, hollowSides)
        for prop in [ 'topShear',
                      'holeSize',
                     'taper']:
            setattr(p, "_"+prop+"X", getattr(props, prop)[0])
            setattr(p, "_"+prop+"Y", getattr(props, prop)[1])

        for prop in [ 'pathCut',
                     'twist']:
            setattr(p, "_"+prop+"Begin", getattr(props, prop)[0])
            setattr(p, "_"+prop+"End", getattr(props, prop)[1])

        for prop in ['skew',
                     # 'dimpleBegin',
                     # 'dimpleEnd',
                        'revolutions',
                        'stepsPerRevolution']:
            setattr(p, "_"+prop, getattr(props, prop))


        p._viewerMode = True
        p._radius = props.radius

        if props.extrapolationType == 'LINEAR':
            p.Extrude(PathType.Linear)
        elif props.extrapolationType == 'FLEXIBLE':
            p.Extrude(PathType.Flexible)
        else:
            p.Extrude(PathType.Circular)
        print(p.ParamsToDisplayString())

        for obj in self._parent.getSelected():
            obj.data.name = "tobdeleted"
            obj.data = self.apply_prim(p, obj.data)

    def apply_prim(self, p, oldmesh=None):
        viewerMode = True
        coords = p._coords
        mesh = bpy.data.meshes.new('prim')
        for coord in coords:
            mesh.vertices.add(1)
            mesh.vertices[-1].co = (coord.X, coord.Y, coord.Z)
        i = 0
        if viewerMode:
            faces = p._viewerFaces
            mesh.faces.add(faces.Count)
            uv = mesh.uv_textures.new("UVTex").data
            while i < faces.Count:
                face = faces[i]
                f = mesh.faces[i]
                f.use_smooth = True
                f.vertices_raw = (face.coordIndex1, face.coordIndex2,
                                               face.coordIndex3, 0)
                uv[i].uv1 = face.uv1.asList()
                uv[i].uv2 = face.uv2.asList()
                uv[i].uv3 = face.uv3.asList()
                i += 1
        else:
            faces = p._faces
            mesh.faces.add(faces.Count)
            while i < faces.Count:
                face = faces[i]
                f = mesh.faces[i]
                f.use_smooth = True
                f.vertices_raw = (face.v1, face.v2,
                                               face.v3, 0)
                i += 1

        if oldmesh:
            for prop in dir(mesh.opensim.prim):
                try:
                    setattr(mesh.opensim.prim, prop, getattr(oldmesh.opensim.prim, prop))
                except AttributeError:
                    pass
        mesh.calc_normals()
        return mesh

    def processCoarseLocationUpdate(self, agent_id, pos):
        """
        A coarse location update arrived from the sim.
        """
        #print("COARSE LOCATION UPDATE", agent_id, pos)
        pass

    def draw_object(self, box, editor, obj):
        if not self.expand(box):
            return

        props = obj.data.opensim.prim
        box = box.box()
        box.label(text="Prim Parameters")
        box.prop(props, 'extrapolationType')
        box.prop(props, 'sides', icon='MOD_DISPLACE')
        box.prop(props, 'hollowSides')
        box.prop(props, 'hollow', icon='PROP_CON')
        row = box.row()
        row.prop(props, 'profile', icon='SURFACE_NCURVE')
        row = box.row()
        row.prop(props, 'twist', icon='FORCE_VORTEX')
        row = box.row()
        row.prop(props, 'topShear', icon='MOD_SIMPLEDEFORM')
        row = box.row()
        row.prop(props, 'pathCut', icon='CURVE_BEZCURVE')
        row = box.row()
        row.prop(props, 'taper')
        # row = box.row()
        # row.prop(props, 'dimpleBegin')
        # row.prop(props, 'dimpleEnd')
        if props.extrapolationType == 'CIRCULAR':
            box.prop(props, 'radius')
            box.prop(props, 'skew', icon='FORCE_MAGNETIC')
            row = box.row()
            row.prop(props, 'holeSize')
            box.prop(props, 'revolutions')
            box.prop(props, 'stepsPerRevolution')
        row = box.row()
        op = box.operator('b2rex.genprim', icon='MESH_ICOSPHERE')


