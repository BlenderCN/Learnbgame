# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import imp
if 'JAFilesystem' in locals():
    imp.reload( JAFilesystem )
else:
    from . import JAFilesystem
if 'JAStringhelper' in locals():
    imp.reload( 'JAStringhelper' )
else:
    from . import JAStringhelper

import bpy

class MaterialManager():
    def __init__(self):
        self.basepath = ""
        self.materials = {}
        self.guessTextures = False
        self.useSkin = False
        self.initialized = False
    
    def init(self, basepath, skin_rel, guessTextures):
        self.basepath = basepath
        self.guessTextures = guessTextures
        if skin_rel != "":
            succes, skin_abs = JAFilesystem.FindFile(skin_rel, self.basepath, ["skin"])
            try:
                file = open(skin_abs, mode="r")
            except IOError:
                print("Could not open file: ", skin_rel, sep="")
                return False, "Could not open skin!"
            self.skin = {}
            for line in file:
                pos = line.find(',')
                if pos != -1:
                    self.skin[line[:pos].strip()] = line[pos+1:].strip()
            self.useSkin = True
        self.initialized = True
        return True, ""
    
    def getMaterial(self, name, bsShader):
        assert(self.initialized)
        # "fix" removed textures (which should force using .skin file)
        if self.guessTextures:
            #I don't need to fix nomaterial - empty materials don't get loaded anyway.
            #if bsShader[:12] == b"\0nomaterial]":
            #    bsShader = b""
            if bsShader[:7] == b"\0odels/":
                bsShader = b"models/" + bsShader[7:]
        shader = JAStringhelper.decode(bsShader)
        if self.useSkin:
            if name in self.skin:
                shader = self.skin[name]
        if shader.lower() == "[nomaterial]" or shader == "" or shader == "*off":
            return
        if shader.lower() in self.materials:
            return self.materials[shader.lower()]
        # create material, it doesn't exist yet
        mat = bpy.data.materials.new(shader)
        self.materials[shader.lower()] = mat
        # try to find the image
        success, path = JAFilesystem.FindFile(shader, self.basepath, ["jpg", "png", "tga"])
        # if it doesn't exist, we're done.
        if not success:
            print("Texture not found: \"", shader, "\"", sep="")
            # make it pink though
            mat.diffuse_color = (1, 0, 1)
            return mat
        
        #load image
        img = bpy.data.images.load(path)
        #create a texture with it
        tex = bpy.data.textures.new(shader, type='IMAGE')
        tex.image = img
        # create texture slot
        tex_slot = mat.texture_slots.add()
        tex_slot.texture_coords = 'UV'
        tex_slot.texture = tex
        
        return mat
