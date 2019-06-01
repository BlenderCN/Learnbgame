// Filename: bpbObject.cxx
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

#include "bpbObject.h"
#include "bpbObjectData.h"

////////////////////////////////////////////////////////////////////
//     Function: BPBObject::set_data
//       Access: Public
//  Description: Changes the data block associated with this object.
////////////////////////////////////////////////////////////////////
void BPBObject::
set_data(BPBObjectData *data) {
  if (data == _data) {
    return;
  }
  if (_data != NULL) {
    //_data->_objects.erase(this);
  }
  if (data != NULL) {
    data->_objects.insert(this);
  }
  _data = data;
}

////////////////////////////////////////////////////////////////////
//     Function: BPBObject::set_parent
//       Access: Public
//  Description: Changes the parent object of this object.
////////////////////////////////////////////////////////////////////
INLINE void BPBObject::
set_parent(BPBObject *parent) {
  _parent = parent;
}

////////////////////////////////////////////////////////////////////
//     Function: BPBObject::get_node
//       Access: Public
//  Description: Returns a PandaNode for this object.
////////////////////////////////////////////////////////////////////
PandaNode *BPBObject::
get_node() {
  //TODO
  if (_node == NULL) {
    if (_type == MAKE_ID2('M', 'E')) {
      _node = new GeomNode(_name);
    } else {
      _node = new PandaNode(_name);
    }
  }
  return _node;
}

////////////////////////////////////////////////////////////////////
//     Function: BPBObject::update
//       Access: Public, Virtual
//  Description: Called by the bridge when the corresponding Blender
//               object might have changed.
////////////////////////////////////////////////////////////////////
void BPBObject::
update(DNA_ID *dna_id) {
  BPBID::update(dna_id);
}
