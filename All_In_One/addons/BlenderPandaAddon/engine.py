import bpy

from .realtime_engine.engine import RealTimeEngine


class PandaEngine(RealTimeEngine):
	bl_idname = 'PANDA3D'
	bl_label = "Panda3D"