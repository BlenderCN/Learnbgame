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

import bpy
import os

from . import fbx
from . import fbx_basic
from .fbx_basic import *
from .fbx_props import *
from .fbx_model import *
from . import fbx_data

#------------------------------------------------------------------
#   Global strings
#------------------------------------------------------------------

Header1 = (
"""; FBX 7.3.0 project file
; 
; 
; ----------------------------------------------------

FBXHeaderExtension:  {
    FBXHeaderVersion: 1003
    FBXVersion: 7300
    CreationTimeStamp:  {
        Version: 1000
        Year: 2013
        Month: 1
        Day: 13
        Hour: 12
        Minute: 3
        Second: 42
        Millisecond: 977
    }
    Creator: "FBX SDK/FBX Plugins version 2013.3"
    SceneInfo: "SceneInfo::GlobalInfo", "UserData" {
        Type: "UserData"
        Version: 100
        MetaData:  {
            Version: 100
            Title: ""
            Subject: ""
            Author: ""
            Keywords: ""
            Revision: ""
            Comment: ""
        }
        Properties70:  {
""")
Header2 = (
"""
            P: "Original", "Compound", "", ""
            P: "Original|ApplicationVendor", "KString", "", "", ""
            P: "Original|ApplicationName", "KString", "", "", ""
            P: "Original|ApplicationVersion", "KString", "", "", ""
            P: "Original|DateTime_GMT", "DateTime", "", "", ""
            P: "Original|FileName", "KString", "", "", ""
            P: "LastSaved", "Compound", "", ""
            P: "LastSaved|ApplicationVendor", "KString", "", "", ""
            P: "LastSaved|ApplicationName", "KString", "", "", ""
            P: "LastSaved|ApplicationVersion", "KString", "", "", ""
            P: "LastSaved|DateTime_GMT", "DateTime", "", "", ""
        }
    }
}
""")

GlobalSettings = (
"""
GlobalSettings:  {
    Version: 1000
    Properties70:  {
        P: "UpAxis", "int", "Integer", "",1
        P: "UpAxisSign", "int", "Integer", "",1
        P: "FrontAxis", "int", "Integer", "",2
        P: "FrontAxisSign", "int", "Integer", "",1
        P: "CoordAxis", "int", "Integer", "",0
        P: "CoordAxisSign", "int", "Integer", "",1
        P: "OriginalUpAxis", "int", "Integer", "",-1
        P: "OriginalUpAxisSign", "int", "Integer", "",1
        P: "UnitScaleFactor", "double", "Number", "",1
        P: "OriginalUnitScaleFactor", "double", "Number", "",1
        P: "AmbientColor", "ColorRGB", "Color", "",0,0,0
        P: "DefaultCamera", "KString", "", "", "Producer Perspective"
        P: "TimeMode", "enum", "", "",0
        P: "TimeSpanStart", "KTime", "Time", "",0
        P: "TimeSpanStop", "KTime", "Time", "",46186158000
        P: "CustomFrameRate", "double", "Number", "",-1
    }
}
""")

DocumentDescription = (
"""
; Documents Description
;------------------------------------------------------------------

Documents:  {
    Count: 1
    Document: 999, "", "Scene" {
        Properties70:  {
            P: "SourceObject", "object", "", ""
            P: "ActiveAnimStackName", "KString", "", "", ""
        }
        RootNode: 0
    }
}
""")

DocumentReferences = (
"""
; Document References
;------------------------------------------------------------------

References:  {
}
""")

#------------------------------------------------------------------
#   Definitions
#------------------------------------------------------------------

def writeDefinitions(fp, nodes):
    definitions = {
        "GlobalSettings" : Definition("\n", 1),
        "Model" : Definition(CModel.propertyTemplate, -1),
    }
    
    for node in nodes:
        if node.active or fbx.settings.writeAllNodes:
            node.addDefinition(definitions)
            
    fp.write(
"""    
; Object definitions
;------------------------------------------------------------------

Definitions:  {
    Version: 100
""")

    n = 0
    for defi in definitions.values():
        n += defi.count
    fp.write('    Count: %d\n' % n)

    for name,defi in definitions.items():
        if fbx.settings.includePropertyTemplates:
            template = defi.template
        else:
            template = "\n"
        fp.write(
            '    ObjectType: "%s" {\n' % (name) +
            '        Count: %d' % defi.count +
            template +
            '    }\n')

    fp.write('}\n')            
        
#------------------------------------------------------------------
#   Export
#------------------------------------------------------------------
    
def exportFbxFile(context, filepath, scale=1.0, encoding='utf-8'):    
    fbx.settings.scale= scale
    fbx.settings.encoding = encoding
    fbx.setCsysChangers()
    filepath = filepath.replace('\\','/')
    try:
        fbx.filepath = filepath.encode(encoding)
    except UnicodeEncodeError:
        filepath = filepath.encode('utf-8', 'replace')
        fbx.message('Cannot encode "%s" with %s codec.' % (filepath, encoding))
        return
    fbx.message('Export "%s"' % fbx.filepath)
    fbx.activeFolder = os.path.dirname(fbx.filepath)

    fbx_data.makeNodes(context)
    fbx_data.makeTakes(context)

    fp = open(filepath, "w")
    fp.write(Header1)    
    fp.write(
        '            P: "DocumentUrl", "KString", "Url", "", "%s"\n' % fbx.filepath +
        '            P: "SrcDocumentUrl", "KString", "Url", "", "%s"' % fbx.filepath )
    fp.write(Header2)    
    fp.write(GlobalSettings)
    fp.write(DocumentDescription)
    fp.write(DocumentReferences)
        
    nodes = fbx.nodes.getAllNodes()
    writeDefinitions(fp, nodes)
    
    fp.write(
"""    
; Object properties
;------------------------------------------------------------------

Objects:  {
""")

    for node in nodes:
        if node.active or fbx.settings.writeAllNodes:
            node.writeFbx(fp)

    fp.write(
"""  
}
; Object connections
;------------------------------------------------------------------

Connections:  {
""")
    
    for node in nodes:
        if node.active or fbx.settings.writeAllNodes:
            node.writeLinks(fp)

    fp.write(
"""    
}
;Takes section
;----------------------------------------------------

Takes:  {
    Current: ""
""")

    for take in fbx.takes.values():
        take.writeFbx(fp)
        
    fp.write(
"""
}
""")
    fp.close()
    fbx.message('File "%s" exported' % filepath)


