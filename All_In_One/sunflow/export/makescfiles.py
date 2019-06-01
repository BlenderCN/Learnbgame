# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
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
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender Version                     2.68
# Exporter Version                    0.0.4
# Created on                          19-Jul-2013
# Author                              NodeBench
# --------------------------------------------------------------------------

import os
import bpy
from .services import is_dupli_child
from ..outputs import sunflowLog


class SunflowSCFileSerializer():
    
    def __init__(self, dictionary, filepath, scenename, framenumber):
        self._di = dictionary
        self._sn = scenename
        self._fn = framenumber
        self._fp = filepath
        self._dp = None
        self._fh = None
        self._name = None
        self._includes = set()
        self._inclf = None
        self._objlist = []

    def _makeFileName(self):
        '''creates the "_include" folder from scene name and frame number'''
        self._name = ("%s.%03d" % (self._sn , self._fn))
        self._inclf = os.path.join(self._dp , "_include." + self._name)
        if not os.path.exists(self._inclf):
            os.makedirs(self._inclf)
    
    def _write_output_block(self, int_blk=[], def_block=[], fnl_blk=[], filename="", def_block_file=True):
        '''write to file object from the string list'''
        pushout = open(filename , 'a')
        for lines in int_blk:
            pushout.write("\n%s" % lines)
        if def_block_file:
            for lines in def_block:
                pushout.write("%s" % lines)
        else:
            for lines in def_block:
                pushout.write("\n%s" % lines)
        for lines in fnl_blk:
            pushout.write("\n%s" % lines)
        pushout.close()
    
    
    def _writable(self, filename):
        '''check if the program able to write to the specified folder/file'''
        try:
            pushout = open(filename , 'a')
            pushout.close()
            return True
        except Exception as error:
            sunflowLog("unable to write to file location %s " % error)
            return False
    
    def _getFolderPath_depreciated(self):
        '''retrive the folder path from the blend filepath, return True if success'''
        self._dp , self._ne = os.path.split(self._fp)
        self._dp = os.path.abspath(self._dp)
        self._ne = self._ne.split('.')[:-1]
        return os.path.exists(self._dp)        
        
    def _getFolderPath(self):
        '''retrive the folder path from the blend filepath, return True if success'''
        self._dp = self._fp
        return os.path.exists(self._dp)  
    
    def _getObjectsList(self):
        '''convert the ExportedObjects dictionary keys to a list'''
        obj = []
        for keys in self._di['ExportedObjects'].keys():
            obj.append((self._di['ExportedObjects'][keys]['parent'] , keys))
        obj.sort()
        self._objlist = obj[:]
        
    def _cleanFolder(self):
        '''clear the .geo and .ins files specific to this export, will not delete the folder'''
        for obj in self._objlist:
            filename = os.path.join(self._inclf , "%s.geo.sc" % (obj[0]))
            if os.path.exists(filename):
                os.remove(filename)
            filename = os.path.join(self._inclf , "%s.ins.sc" % (obj[0]))
            if os.path.exists(filename):
                os.remove(filename)  
    
    
    def _populate_MeshLightObjects(self):
        '''Identifies the Objects which are assigned with a light shader'''
        if 'Shaderlight' not in self._di.keys():
            return
        light_mat = self._di['Shaderlight'].keys()
        if len(light_mat) <= 0:
            return
        exported = self._di['ExportedObjects']
        
        for obj in exported.keys():
            expmat = exported[obj]['materials']
            found = { mat:index for index, mat in enumerate(light_mat) if mat in expmat}
            if len(found) > 0:
                self._di['MeshLightObjects'][exported[obj]['parent']] = found
        
        
    def _populate_modifiers(self):
        '''fill up the blank modifier list with modifiers if not supply with None'''
        if 'Shadermodifier' not in self._di.keys():
            return 
        mod_mat = self._di['Shadermodifier'].keys()
        exported = self._di['ExportedObjects']
        for obj in exported.keys():
            expmat = exported[obj]['materials']
            mod_list = []
            for mat in expmat:
                if mat in mod_mat:
                    mod_list.append(mat)
                else:
                    mod_list.append("None")
            exported[obj]['modifiers'] = mod_list[:]
    
    def _compileObjectBlocks(self):
        '''sorting the output which are light objects or mesh objects'''
        for objs in self._objlist:
            main_file, sub_file = objs
            if sub_file in self._di['MeshLightObjects'].keys():
                self.__compileObjectBlocksLight(objs)
                continue
            if sub_file in self._di['ExportedObjects'].keys():
                self.__compileObjectBlocksNormal(objs)
                continue

    def _compileLightsBlock(self):
        '''write light block to .sc file''' 
        key = 'lamp'
        if key not in self._di.keys():
            return
        for ekey in self._di[key].keys():
            block = self._di[key][ekey]
            self._write_output_block(block, [""] , [] , self._fh, False)
    
    def _compileCameraBlock(self):
        '''write camera block to .sc file'''
        key = 'Camera'
        if key not in self._di.keys():
            return
        for ekey in self._di[key].keys():
            block = self._di[key][ekey]
            self._write_output_block(block, [""] , [] , self._fh, False)
    
    def _compileIncludes(self):
        '''write include files to .sc file'''
        self._includes
        inclu = [(files[-6:], files) for files in self._includes]
        inclu.sort()
        block = []
        for inc in inclu:
            name = ' "%s%s\%s"' % ("_include." , self._name, inc[1])
            block.append("%s %s %s" % ("include" , "", name))
        self._write_output_block(block, [""] , [] , self._fh, False)
    
    
    def _compileLightsWorldBlock(self):
        '''write world light block to .sc file'''
        key = 'world'
        if key not in self._di.keys():
            return
        if 'worldlight' not in self._di[key].keys():
            return
        block = self._di[key]['worldlight']
        self._write_output_block(block, [""] , [] , self._fh, False)


    def _comipleShaderBlock(self):
        '''write shader block to .sc file'''
        if 'Shader' not in self._di.keys():
            sunflowLog("No materials found on this scene.")
            return
        shader = self._di['Shader'].keys()
        for each_shader in shader:
            block = self._di['Shader'][each_shader]
            self._write_output_block(block, [""] , [] , self._fh, False)
    
    
    def _comipleModifierBlock(self):
        '''write Shadermodifier block to .sc file'''
        if 'Shadermodifier' not in self._di.keys():
            sunflowLog("No modifier found on this scene.")
            return
        shader = self._di['Shadermodifier'].keys()
        for each_shader in shader:
            block = self._di['Shadermodifier'][each_shader]
            self._write_output_block(block, [""] , [] , self._fh, False)    
    
    
    def _comipleGlobalIllumination(self):
        '''write Global Illumination block to .sc file'''
        key = 'gi'
        if key not in self._di.keys():
            return
        if 'illumination' not in self._di[key].keys():
            return
        block = self._di[key]['illumination']
        self._write_output_block(block, [""] , [] , self._fh, False)
    
    
    def _comipleOverideGlobalIllumination(self):
        '''write Global Illumination Overide block to .sc file'''
        key = 'override'
        if key not in self._di.keys():
            return
        if 'override' not in self._di[key].keys():
            return
        block = self._di[key]['override']
        self._write_output_block(block, [""] , [] , self._fh, False)
    
    
    def _writeHeader(self, file_path_sc):
        header = []
        header.append('/* Sunflow Open Source Rendering System v0.07.3 Scene File */')
        header.append('/* Generated from blender v%s File: %r */' % (bpy.app.version_string, os.path.basename(bpy.data.filepath)))
        header.append('/* http://sunflow.sourceforge.net/ */\n')
        self._write_output_block(header, [""] , [] , self._fh, False)
        

    
    
    def _compileMainBlock(self):
        '''write the main .sc file'''
        self._name = ("%s.%03d" % (self._sn , self._fn))
        self._fh = os.path.join(self._dp , "%s.sc" % self._name)
        if not os.path.exists(self._fh):
            self._writable(self._fh)
        else:
            os.remove(self._fh)
        
        self._writeHeader(self._fh)
        
        key_list = ['output', 'trace' , 'background' , 'bucket' , 'caustics' ]

        for key in key_list:
            if key not in self._di.keys():
                continue
            if key not in self._di[key].keys():
                continue
            block = self._di[key][key]
            self._write_output_block(block, [""] , [] , self._fh, False)
        
        self._comipleGlobalIllumination()
        self._comipleOverideGlobalIllumination()
        self._comipleShaderBlock()
        self._comipleModifierBlock()
        self._compileLightsBlock()
        self._compileLightsWorldBlock()
        self._compileCameraBlock()
        self._compileIncludes()
    

    def _compileInstanceBlocks(self):
        '''write instances to .ins.sc file'''
        for instancess in self._di['Instantiated'].keys():
            fname = "%s.ins.sc" % instancess
            filename = os.path.join(self._inclf , fname)
            if os.path.exists(filename):
                os.unlink(filename)
        for instancess in self._di['Instantiated'].keys():
            ins_names = [ instblock for instblock in self._di['Instances'].keys() if instblock.split('.inst.')[0] == instancess]
            for each_inst in ins_names:
                act_inst = []
                indent = 0
                space = "        "
                 
                ins = self._di['Instances'][each_inst]
                # sunflowLog(ins)
                original_obj = ins['pname']
                int_blk = []  

                if original_obj in self._di['ExportedObjects'].keys():
                    block_dirct = self._di['ExportedObjects'][original_obj]                    
                    indent += 1 
                    num_of_shaders = len(block_dirct['materials'])
                    if  num_of_shaders > 1:
                        int_blk.append("%s %s %s" % (space * indent , "shaders", num_of_shaders))
                        indent += 1
                        for each_shdr in block_dirct['materials']:
                            int_blk.append("%s %s %s" % (space * indent , "", each_shdr))
                        indent -= 1
                    else:
                        int_blk.append("%s %s %s" % (space * indent , "shader", block_dirct['materials'][0]))
                     
                     
                    num_of_shaders = len(block_dirct['modifiers'])
                    if  num_of_shaders > 1:
                        int_blk.append("%s %s %s" % (space * indent , "modifiers", num_of_shaders))
                        indent += 1
                        for each_shdr in block_dirct['modifiers']:
                            int_blk.append("%s %s %s" % (space * indent , "", "%s.m" % each_shdr))
                        indent -= 1
                    else:
                        int_blk.append("%s %s %s" % (space * indent , "modifier", "%s.m" % block_dirct['modifiers'][0]))
                    indent -= 1
                     

                act_inst.append("%s %s %s" % (space * indent , "instance", "{"))
                indent += 1 
                act_inst.append("%s %s %s" % (space * indent , "name", ins['iname']))
                act_inst.append("%s %s %s" % (space * indent , "geometry", ins['pname']))
                ln = len(ins['trans'])
                if ln == 1:
                    act_inst.append("%s %s %s" % (space * indent , "transform  row", ' '.join(ins['trans'][0])))
                else:
                    act_inst.append("%s %s %s" % (space * indent , "transform", ""))
                    act_inst.append("%s %s %s" % (space * indent , "steps", ln))
                    act_inst.append("%s %s %s" % (space * indent , "times", " 0.0 1.0"))                
                    for exh in range(ln):
                        act_inst.append("%s %s %s" % (space * indent , "row", ' '.join(ins['trans'][exh]))) 
                act_inst.extend(int_blk)
                indent -= 1 
                act_inst.append("%s %s %s" % (space * indent , "}", ""))
                
                fname = "%s.ins.sc" % instancess
                filename = os.path.join(self._inclf , fname)
                if not self._writable(filename):
                    return
                self._write_output_block(act_inst, [], [], filename, False)        
                self._includes.add(fname)             

    def __compileObjectBlocksNormal(self, objs):
        '''write objects to .geo.sc file'''
        try:
            main_file, sub_file = objs
            block_dirct = self._di['ExportedObjects'][sub_file]
            int_blk = [] 
            indent = 0
            space = "        "
            
            int_blk.append("%s %s %s" % (space * indent , "object", "{"))
            indent += 1
            
            if not is_dupli_child(sub_file):        
                num_of_shaders = len(block_dirct['materials'])
                if  num_of_shaders > 1:
                    int_blk.append("%s %s %s" % (space * indent , "shaders", num_of_shaders))
                    indent += 1
                    for each_shdr in block_dirct['materials']:
                        int_blk.append("%s %s %s" % (space * indent , "", each_shdr))
                    indent -= 1
                else:
                    int_blk.append("%s %s %s" % (space * indent , "shader", block_dirct['materials'][0]))        
                
                num_of_shaders = len(block_dirct['modifiers'])
                if  num_of_shaders > 1:
                    int_blk.append("%s %s %s" % (space * indent , "modifiers", num_of_shaders))
                    indent += 1
                    for each_shdr in block_dirct['modifiers']:
                        int_blk.append("%s %s %s" % (space * indent , "", "%s.m" % each_shdr))
                    indent -= 1
                else:
                    int_blk.append("%s %s %s" % (space * indent , "modifier", "%s.m" % block_dirct['modifiers'][0]))
                
                num_of_transforms = len(block_dirct['trans_mat']) 
                if num_of_transforms > 0 :
                    int_blk.append("%s %s %s" % (space * indent , "transform", ""))
                    int_blk.append("%s %s %s" % (space * indent , "steps ", num_of_transforms))
                    int_blk.append("%s %s %s" % (space * indent , "times", " 0.0 1.0"))
                    indent += 1
                    # FIXME: error on joined duplis will look later if bug reapprears                
                    for each_trn in block_dirct['trans_mat']:
                        int_blk.append("%s %s %s" % (space * indent , "row", ' '.join(each_trn)))
                    indent -= 1
                    
            else:
                int_blk.append("%s %s %s" % (space * indent , "noinstance", ""))
                
                
            int_blk.append("%s %s %s" % (space * indent , "type", "generic-mesh"))
            int_blk.append("%s %s %s" % (space * indent , "name", sub_file))
            
            fnl_blk = []
            fnl_blk.append("%s %s %s" % (space * indent , "}", ""))
            
            def_block = block_dirct['objectfile']
            if not os.path.exists(def_block):
                return
            def_block_handle = open(def_block , 'r')
            fname = "%s.geo.sc" % main_file
            filename = os.path.join(self._inclf , fname)
            if not self._writable(filename):
                return
            self._write_output_block(int_blk, def_block_handle, fnl_blk, filename, True)    
            def_block_handle.close()    
            self._includes.add(fname)
        except Exception as error:
            sunflowLog("Ignoring object %s due to the following error" % str(objs))
            sunflowLog(error)

    def __compileObjectBlocksLight(self, objs):
        '''write light block to .geo.sc file'''     
        try:
            main_file, sub_file = objs
            block_dirct = self._di['ExportedObjects'][sub_file]
            int_blk = [] 
            indent = 0
            space = "        "
            
            int_blk.append("%s %s %s" % (space * indent , "light", "{"))
            indent += 1
            
            int_blk.append("%s %s %s" % (space * indent , "type", "meshlight"))
            int_blk.append("%s %s %s" % (space * indent , "name", sub_file))
            
            mat = [ mat for mat in self._di['MeshLightObjects'][sub_file].keys()][0]
            desc = self._di['Shaderlight'][mat]
            
            int_blk.extend(desc)
            
            fnl_blk = []
            fnl_blk.append("%s %s %s" % (space * indent , "}", ""))
            
            def_block = block_dirct['objectfile']
            if not os.path.exists(def_block):
                return
            def_block_handle = open(def_block , 'r')
            datablock = []
            for eachline in def_block_handle:
                splt = eachline.split()
                if (('normals' in splt) | ('uvs' in splt) | ('face_shaders' in splt)):
                    break
                datablock.append(eachline)
            
            fname = "%s.geo.sc" % main_file
            filename = os.path.join(self._inclf , fname)
            if not self._writable(filename):
                return
            self._write_output_block(int_blk, datablock, fnl_blk, filename, False)    
            def_block_handle.close()    
            self._includes.add(fname)
        except Exception as error:
            sunflowLog("Ignoring object %s due to the following error" % str(objs))
            sunflowLog(error)
        
  
    def debugPrintDictionary(self):   
        '''print the contents of the dictionary to console'''        
        sunflowLog("{")
        for keys in self._di.keys():
            sunflowLog("'%s':" % keys)
            sunflowLog(self._di[keys])
            sunflowLog(",")
        sunflowLog("}")
        
    def debugPrintExportedObjects(self):
        '''print the names of the objects which are exported'''
        for keys in self._di['ExportedObjects'].values():
            sunflowLog(keys)


    def _deleteTempFiles(self):
        '''removes the temp files created in the export process'''
        for objs in self._objlist:
            dummy_file, sub_file = objs
            if sub_file in self._di['ExportedObjects'].keys():
                path = self._di['ExportedObjects'][sub_file]['objectfile']
                if os.path.exists(path) :
                    # sunflowLog("path >> %s" % path)
                    os.unlink(path)
    

    def _compileHairBlock(self):
        if 'hair' not in self._di.keys():
            return
        for hair in self._di['hair'].keys():
            fname = "%s.par.sc" % hair
            filename = os.path.join(self._inclf , fname)
            if os.path.exists(filename):
                os.unlink(filename)
                
        for hair in self._di['hair'].keys():            
            file_ = self._di['hair'][hair]['path']
            fileobj = open(file_, 'r')
            fname = "%s.par.sc" % hair
            filename = os.path.join(self._inclf , fname)
            if not self._writable(filename):
                return
            self._write_output_block([], fileobj, [], filename, True)     
            fileobj.close()   
            self._includes.add(fname)    
        
    
    
    def makeSunflowSCFiles(self):
        '''Call this method to generate the .sc, .geo.sc, .ins.sc files'''
        if not self._getFolderPath():
            return False
        self._populate_MeshLightObjects()
        self._populate_modifiers()
        self._getObjectsList()
        self._makeFileName()
        self._cleanFolder()
        self._compileObjectBlocks()
        self._compileInstanceBlocks()
        self._compileHairBlock()
        self._compileMainBlock()
        
        self.debugPrintDictionary()
        
        self._deleteTempFiles()
        return True
        
        

def testmod():
    pass
#     ass = SunflowSCFileSerializer(dictionary, filepath, scenename, framenumber)
#     ass.makeSunflowSCFiles()


if __name__ == '__main__':
    testmod()
