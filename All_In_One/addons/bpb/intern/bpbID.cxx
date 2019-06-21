// Filename: bpbID.cxx
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

#include "bpbID.h"

#include "DNA_ID.h"

////////////////////////////////////////////////////////////////////
//     Function: BPBID::validate
//       Access: Public, Static
//  Description: Makes sure that this is a valid object.
////////////////////////////////////////////////////////////////////
bool BPBID::
validate(BPBID *id) {
  if (id == NULL) {
    return false;
  }
  // Write a more meaningful test here.
  return true;
}

////////////////////////////////////////////////////////////////////
//     Function: BPBID::update
//       Access: Public, Virtual
//  Description: Called by the bridge when the corresponding Blender
//               object might have changed.
////////////////////////////////////////////////////////////////////
void BPBID::
update(DNA_ID *dna_id) {
  nassertd(dna_id != NULL) {
    _name = "<INVALID>";
    return;
  }

  // The first two characters contain the type code.
  char *name = dna_id->name;
  _type_code[0] = name[0];
  _type_code[1] = name[1];
  _name = string(name + 2);

  cerr << "Updating " << _type_code[0] << _type_code[1] << ":" << _name << "\n";
}
