from .find_houdini import find_houdini, append_path

HFS = find_houdini()

if '17.5.258' in HFS:
	append_path(HFS['17.5.258'])
	from . import core_17_5_258 as core
elif '17.5.173' in HFS:
	append_path(HFS['17.5.173'])
	from . import core_17_5_173 as core
elif '17.0.416' in HFS:
	append_path(HFS['17.0.416'])
	from . import core_17_0_416 as core
elif '17.0.352' in HFS:
	append_path(HFS['17.0.352'])
	from . import core_17_0_352 as core
elif '16.5.634' in HFS:
	append_path(HFS['16.5.634'])
	from . import core_16_5_634 as core
else:
	raise 'No valid houdini version found: %s' % HFS.keys()

del append_path
del find_houdini
del HFS

AttribType = core.AttribType
AttribData = core.AttribData
TypeInfo = core.TypeInfo
PrimitiveTypes = core.PrimitiveTypes

Vector2 = core.Vector2
Vector3 = core.Vector3
Vector4 = core.Vector4

Attrib = core.Attrib
Point = core.Point
Vertex = core.Vertex
Polygon = core.Polygon
BezierCurve = core.BezierCurve
NURBSCurve = core.NURBSCurve
Geometry = core.Geometry

__all__ = []
