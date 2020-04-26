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

# <pep8-80 compliant>
# Copyright 2015 Bassam Kurdali 

"""
This module is an alternate to tagging a rig, involves guessing at the type of
action and the type of bones based on the rig hierarchy, bone names/ symmetry, 
and the action itself. NOTE: IK targets or parents of IK targets are considered
deformers or parents of deformers. This includes driver checks (if our location 
drives the location of a deformer or IK target. We need to dig into the hierarchy
for this.

several types of walk action exist:
 1- forward offset walk action
 2- forward offset using parent bone.
 3- in place walk (with stride)
 4- in place walk (without stride)

Properties of action type 1:
 1- one or more bones have non-flat location channels, with the end offsets 
    being in the same world direction, and being similar in length.
 2- there are no channels on the same hierarchy level as our 'feet' that have
    different location offsets, unless they are non deformers with no deforming
    children.

Properties of action type 2:
 1- A single bone has an offset in one world axis only. Check 3.
 2- that bone has children with non-flat location channels but zero location offset.
 3- there are no siblings of the parent bone with animation channels in location, unless those siblings have no deform and no deforming children (maybe they're drivers)

Properties of action type 3:
  1- we can find no top level non flat offsetting location channels with deform 
     or with deforming children
  2- we do find  
 
 

several types of bones can be found in a rig; we can attempt to guess them:

feet (includes body):
 0- exist at topmost level in hierarchy of channels, unless action type 2,
    in which case they are at the second level
 1- finding offsetting bones in an offsetting action,
 2- finding zero offset bones with location keys in a in place action
 3-


Possible steps:

Step 1: look for none flat location channels return loc_channels.
Step 2: tag each loc_channel as deform/non deform based on the criteria:
  1- has deform on.
  2- has children with deform on.
  3- is an IK target.
  4- has children that are IK targets(including poll)
  5- drives location->location of a deform bone (recursive)
  6- drives location->location of a IK target (recursive)
Step 3: tag each loc_channel as offset/ non offset based on changes in world
        location/offset. possibly use a Vector to store this offset.
Step 4: guess action, feet, stride:
        - if we have deforming offsetting channels, with deforming, offsetting
          children, bail.
        - one or more deforming, offsetting that have no deforming, offsetting
          parent loc channels, and no deforming, offsetting child loc_channels
          means we are either type 1 or type 2
        - if more than one, we are type 1, check that we have similar world
          offsets, otherwise bail, and those loc_channels are feet
        - if one only, and it has no non offset siblings,
          and it has deforming non offsetting children 
          (more than one) assume it is a parent and those are feet,
          action type 2
        - if we have one none deform offset channel, and more than one sibling
          deforming non offset channels, it is a stride bone, they are feet, 
          action type 3
        - if we have only top level non offsetting deform channels, we are
          action type 4. assume those are feet, and try to figure out the 
          stride offset.
Step 5: find legs:
        - for the rest of the channels, find out if we are dependant on a foot, 
          and if we are assign to that foot.
        - store none-foot channels as none feet.
Step 6: find dependent feet/body:
        - search for symmetry in feet (left/right) assign props.
        - assume non symetrical feet are bodies.
        - if more than one body, look for string matches in bodies/feet.
        - make bodies dependent on string matching feet, or all feet if no
          string matches.
step 7: assign non-foot channels to first body as a body-leg.
step 8: find IK arms
        - if a foot has no contact pose, assume it is an arm and remove it from 
          dependency of bodies.
step 9: if we are confident tag the rig with our guess
"""


