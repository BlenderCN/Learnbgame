// Filename: bpbContext.I
// Created by:  rdb (20Jan15)
//
////////////////////////////////////////////////////////////////////
//
// PANDA 3D SOFTWARE
// Copyright (c) Carnegie Mellon University.  All rights reserved.
//
// All use of this software is subject to the terms of the revised BSD
// license.  You should have received a copy of this license along
// with this source code in a file named "LICENSE."
//
////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////
//     Function: BPBObject::get_data
//       Access: Public
//  Description: Returns the data block associated with this object.
////////////////////////////////////////////////////////////////////
INLINE BPBObjectData *BPBObject::
get_data() const {
  return _data;
}

////////////////////////////////////////////////////////////////////
//     Function: BPBObject::get_parent
//       Access: Public
//  Description: Returns the parent object, or NULL if there is none.
////////////////////////////////////////////////////////////////////
INLINE BPBObject *BPBObject::
get_parent() const {
  return _parent;
}
