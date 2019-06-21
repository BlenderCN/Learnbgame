from . import Logger as log
import bpy

class F3bContext:
    def __init__(self,cfg,tofile,topath):
        self.cfg=cfg
        self.ids={}
        self.updateNeeded={}
        self.textures=[]    
        self.tofile=tofile
        self.topath=topath
    
    def idOf(self, v):
        vid=None
        if v in self.ids:
            vid=self.ids[v]
        else:
            vid=str(type(v).__name__)+"_"+str(hash(v))
        return vid  

    def setUpdateNeededFor(self, obj):
        vid = self.idOf(obj)
        self.updateNeeded[vid]=True
    
    def checkUpdateNeededAndClear(self,obj):
        vid=self.idOf(obj)
        res=True if not vid in self.updateNeeded else self.updateNeeded[vid]
        self.updateNeeded[vid]=False
        log.debug("%s update needed = %s" % (vid,res))
        return res

    def isExportable(self,obj):
        excluded=True
       
        if excluded:
            cols=obj.users_collection
            for col in cols:
                if col.name in bpy.context.window.view_layer.layer_collection.children:
                    layer=bpy.context.window.view_layer.layer_collection.children[col.name]
                    if not layer.exclude:
                        excluded=False
                        break
                else: excluded=False
        return not excluded and not obj.hide_render and (not self.cfg.optionExportSelection or  obj.select_get() )