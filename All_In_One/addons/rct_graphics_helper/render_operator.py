'''
Copyright (c) 2018 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy
import math
import os

from . render_task import *

class RCTRender(object):

    _timer = None
    rendering = False
    stop = False
    renderTask = None
    
    @classmethod
    def poll(cls, context):
        return bpy.data.objects['Rig'] is not None

    def pre(self, dummy):
        self.rendering = True
    
    def post(self, dummy):
        self.rendering = False
    
    def cancelled(self, dummy):
        self.stop = True
    
    def execute(self, context):
        rotate_rig(context, 0, 0, 0, 0)
        bpy.data.cameras["Camera"].ortho_scale = 169.72 / (100 / bpy.data.scenes['Scene'].render.resolution_percentage)
        
        self.rendering = False
        self.stop = False
        
        bpy.app.handlers.render_pre.append(self.pre)
        bpy.app.handlers.render_post.append(self.post)
        bpy.app.handlers.render_cancel.append(self.cancelled)
        self._timer = context.window_manager.event_timer_add(0.5, context.window)
        context.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}
      
    def modal(self, context, event):  
        if event.type == 'TIMER':
            
            if self.stop or self.renderTask == None or (self.renderTask.status == "FINISHED" and not self.rendering):
                self.finished(context)
                
                return {"FINISHED"}
            
            elif not self.rendering:
                # render next frame
                self.renderTask.step()
                
        return {"PASS_THROUGH"}

    def finished(self, context):
        bpy.app.handlers.render_pre.remove(self.pre)
        bpy.app.handlers.render_post.remove(self.post)
        bpy.app.handlers.render_cancel.remove(self.cancelled)
        context.window_manager.event_timer_remove(self._timer)
                
        rotate_rig(context, 0, 0, 0, 0)
        bpy.data.cameras["Camera"].ortho_scale = 169.72
