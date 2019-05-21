#!/bin/bash

git remote add drawnearest 'git@github.com:chromoly/blender-EditMeshDrawNearest.git'
git remote add lockcoords 'git@github.com:chromoly/blender_lock_coords.git'
git remote add lockcursor3d 'git@github.com:chromoly/lock_cursor3d.git'
git remote add mousegesture 'git@github.com:chromoly/blender_mouse_gesture.git'
git remote add overwrite_builtin_images 'git@github.com:chromoly/blender-OverwriteBuiltinImages.git'
git remote add quadview_move 'git@github.com:chromoly/quadview_move.git'
git remote add regionruler 'git@github.com:chromoly/regionruler.git'
git remote add screencastkeys 'git@github.com:chromoly/blender-ScreencastKeysMod.git'
git remote add updatetag 'git@github.com:chromoly/blender_update_tag.git'

git subtree add --prefix=drawnearest drawnearest master --squash
git subtree add --prefix=lockcoords lockcoords master --squash
git subtree add --prefix=lockcursor3d lockcursor3d master --squash
git subtree add --prefix=mousegesture mousegesture master --squash
git subtree add --prefix=overwrite_builtin_images overwrite_builtin_images master --squash
git subtree add --prefix=quadview_move quadview_move master --squash
git subtree add --prefix=regionruler regionruler master --squash
git subtree add --prefix=screencastkeys screencastkeys master --squash
git subtree add --prefix=updatetag updatetag master --squash

