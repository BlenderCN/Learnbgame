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


# CRC
# linux
#   2.59 r39307, patch v.0.72
#     original :
#        addon_utils.py    : 568c0665
#        space_userpref.py : 59fd7165
#     modded :
#        addon_utils.py    : 955d7c4c
#        space_userpref.py : be762ba6


bl_info = {
    "name": "addon dependencies",
    "description": "reload wip multi-file addons without restarting, relationship check for addon... see wiki",
    "author": "Littleneo / Jerome Mahieux",
    "version": (0, 75),
    "blender": (2, 63, 1),
    "api": 39307,
    "location": "",
    "warning": "only handy for python addon programming",
    "wiki_url": "https://github.com/littleneo/Blender-addon-dependencies/blob/master/addon/addon_dependencies/README",
    "tracker_url": "https://github.com/littleneo/Blender-addon-dependencies/issues",
    "category": "Development"
}

import os
import shutil
from sys import modules
from zlib import crc32
from addon_dependencies.fs_tools import *
from . config import *

# Addon dependencies folder
ad_path = clean(modules['addon_dependencies'].__path__[0]) + '/'


# blender python files (/scripts)
bp_path = clean(bpy.utils.script_paths()[0]) + '/'


## returns state and and a message
# state is either 'ori', 'mod', 'mod mismatch', 'mismatch' or 'missing'
def _checkstate(revision,verbose=False) :
    revision_mod = revision_mod_source(revision)
    if verbose :
        print('    checking file for r%s...'%revision)
        if revision_mod != revision : print('    aliased : %s is actually used as patch source'%revision_mod)
    for fid, mod in enumerate(modded[revision_mod]) :
        filename = mod.split('/')[-1]
        # files exist ?
        exist = isfile(bp_path + mod)
        if verbose : print('    %s : %s'%(filename, 'found' if exist else 'missing'))
        if exist == False :
            return 'missing', '%s missing'%filename
        # which version of this file is running ?
        # all files are either modded or original, no mix allowed
        fb = open(bp_path + mod,'rb')
        crc = format( crc32(fb.read()) & 0xFFFFFFFF, '08x')
        fb.close()
        
        f = open(bp_path + mod)
        modline = f.readlines()[19][:-1]
        f.close()
        # this is a modded file
        if 'lnmod =' in modline :
            if verbose : print('    modded : %s (crc : %s)'%(modline,crc))
            if modline == 'lnmod = (%s,%s)'%(revision_mod, patch_version) or modline == "lnmod = ('%s',%s)"%(revision_mod, patch_version) :
                if fid == 0 : version = 'mod'
                elif version != 'mod' : return 'mismatch', 'original and modded files are mixed !'
            # this is a modded file from a previous version
            else :
                return 'mod mismatch', '%s modded version does not match'%filename

        # else an original user file
        else :
            if verbose : print('    original (crc : %s)'%crc)
            if fid == 0 : version = 'ori'
            elif version != 'ori' : return 'mismatch', 'original and modded files are mixed !'
    return version, 'currently using the %s files'%('modded' if version == 'mod' else 'original')

def revision_mod_source(revision) :
    if revision in modded and type(modded[revision][0]) == int :
        return str(modded[revision][0])
    return revision
    
def mismatch_log() :
    compat = ''
    for rev in modded.keys() : compat += rev+', '
    M,m,s = bpy.app.version
    print('  version mismatch :')
    print('  this addon is compatible with blender revision%s %s'%('s' if len(modded) > 1 else '', compat))
    print('  but you currently use blender v%s.%s.%s revision %s.'%(M,m,s,bpy.app.build_revision))

def register() :
    print('\naddon dependencies v%s.%s :'%(bl_info['version'][0],bl_info['version'][1]))
    if fake_revision :
        revision = revision_real = fake_revision
        print('  ! faked revision switch enabled !')
    else :
        revision_real = bpy.app.build_revision
        if type(revision_real) == bytes :
            revision_real = revision_real.decode()
        revision_real = revision_real.replace(':','-')
        revision = revision_mod_source(revision_real)
    alias = '(alias) ' if revision_real != revision else ''

    # blender version check. version absolutely needs to match an available patch.
    # double check for an existing revision folder in the mod folder and for an existing key in the 'modded' dict above
    for dir in scandir(ad_path + 'mod', filemode = False) :
        # FOUND
        if revision == dir.split('/')[-1] and revision in modded.keys() :
            print('  blender r%s, patch v.%s.%s'%(revision_real, patch_version[0], patch_version[1]))

            # which files are currently used ?
            state, log = _checkstate(revision_real,verbose)
            print('  %s'%log)

            # not the modded ones : install them
            if state != 'mod' :
                revision_path_real = revision_real + '/'
                revision_path = revision + '/'
                
                # revision backup directory
                if isdir( ad_path + 'user/' + revision_path_real ) == False : 
                    os.makedirs( ad_path  + 'user/' + revision_path_real)

                # backup used files if not already done
                print('  Backing up user files :')
                for file_path in modded[revision] :
                    filename = file_path.split('/')[-1]
                    if isfile( ad_path + 'user/' + revision_path_real + filename ) == False :
                        print('    copying %s file in user/%s'%(filename, revision_real))
                        if verbose :
                            print('      from : ' + bp_path + file_path )
                            print('      to   : ' + ad_path + 'user/' + revision_path_real + filename )
                        shutil.copy2( bp_path + file_path , ad_path + 'user/' + revision_path_real + filename )
                    else :
                        print('    %s already exists in user/%s'%(filename, revision_real))
                
                # copy modded files
                print('  Patching %s:'%alias)
                for file_path in modded[revision] :
                    filename = file_path.split('/')[-1]
                    print('    copying patch from mod/%s/%s'%(revision, filename))
                    if verbose :
                        print('      from : ' + ad_path + 'mod/' + revision_path + filename )
                        print('      to   : ' + bp_path + file_path )
                    shutil.copy2( ad_path + 'mod/' + revision_path + filename, bp_path + file_path )
                print('  patch installed, please restart Blender.\n')
            break
    else :
        # NOT FOUND
        mismatch_log()

def unregister() :
    print('\naddon dependencies v%s.%s :'%(bl_info['version'][0],bl_info['version'][1]))
    global use_user_files
    if fake_revision :
        revision = revision_real = fake_revision
        use_user_files = True
        print('  ! faked revision switch enabled !')
    else :
        revision_real = bpy.app.build_revision
        revision = revision_mod_source(revision_real)
    alias = '(alias) ' if revision_real != revision else ''

    # blender version check. version absolutely needs to match an available patch.
    #double check for an existing revision folder in the mod folder and for an existing key in the 'modded' dict above
    for dir in scandir(ad_path + 'mod', filemode = False) :
        # FOUND
        if revision == dir.split('/')[-1] and revision in modded.keys() :
            print('  blender r%s, patch v.%s.%s'%(revision_real,patch_version[0],patch_version[1]))

            # which file are currently used ?
            state, log = _checkstate(revision_real,verbose)
            print('  %s'%log)

            # not the original ones : install them
            if state != 'ori' :
                revision_path_real = revision_real + '/'
                revision_path = revision + '/'

                # restore previously backuped user files switch is on
                # some checks before to process
                if use_user_files :
                    print('  Restore from the user backup folder :')
                    # revision backup directory does not exist, abort
                    if isdir( ad_path + 'user/' + revision_path_real ) == False : 
                        use_user_files = False
                        print("    can't restore user files, revision folder %s is missing in /user"%(revision_real) )
                    else :

                        # some file are missing in user/revision, abort
                        for file_path in modded[revision] :
                            filename = file_path.split('/')[-1]
                            if isfile(  ad_path + 'user/' + revision_path_real + filename ) == False :
                                print("    can't restore user files, file %s is missing in /user/%s"%(filename,revision_real) )
                                use_user_files = False
                                break
                                
                        # all system go
                        else :
                            for file_path in modded[revision] :
                                filename = file_path.split('/')[-1]
                                print('    restoring user/%s/%s'%(revision_real,filename) )
                                if verbose :
                                    print('      from : ' + ad_path + 'user/' + revision_path_real + filename )
                                    print('      to   : ' + bp_path + file_path )
                                shutil.copy2( ad_path + 'user/' + revision_path_real + filename, bp_path + file_path )
                                os.remove( ad_path + 'user/' + revision_path_real + filename )
                                
                # restore original shipped files (or fall back when user mode failed)
                if use_user_files == False :
                    print('  Restore from the original folder %s:'%alias)
                    for file_path in modded[revision] :
                        filename = file_path.split('/')[-1]
                        print('    restoring ori/%s/%s'%(revision,filename) )
                        if verbose :
                            print('      from : ' + ad_path + 'ori/' + revision_path + filename )
                            print('      to   : ' + bp_path + file_path )
                        shutil.copy2( ad_path + 'ori/' + revision_path + filename, bp_path + file_path )
                print('  patch removed, please restart Blender.\n')

            break
    else :
        # NOT FOUND
        mismatch_log()