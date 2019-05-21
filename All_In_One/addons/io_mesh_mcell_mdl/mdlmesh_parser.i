%module mdlmesh_parser

%{
#define SWIG_FILE_WITH_INIT
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "vector.h"
#include "mdlmesh_parser.h"
%}

%typemap(out) struct object * {
  PyObject *mdlobjModule,*mdlobjDict;
  PyObject *mdlobjClass,*objregClass;
  PyObject *mdlobj,*p_mdlobj,*prev_sib;
  PyObject *arg,*pArgs;
  PyObject *o,*v,*f,*reg, *region_dict,*reg_name,*reg_elements;
  PyObject *viz_value,*set_viz_value;
  PyObject *set_vertices,*set_faces,*set_regions;
  PyObject *set_next,*set_parent,*set_first_child,*set_last_child;
  PyObject *set_object_type;
  double p[1][4];
  int i,j;
  int n_verts,n_faces,n_elements;
  struct object *r_objp,*p_objp,*objp;
  struct region_list *rlp;


  r_objp = $1;


  // Look up your module and get its "dictionary"
  // MODULE_NAME should be the name of your python file (minus the .py)
  // pModule will be a pointer to the module containing your class
  
  mdlobjModule = PyImport_ImportModule("cellblender.io_mesh_mcell_mdl.mdlobj");
  mdlobjDict = PyModule_GetDict(mdlobjModule);

  // Look up your class by name
  // CLASSNAME should be the name of your class
  // the first through nth arguments below must be python objects
  mdlobjClass = PyDict_GetItemString(mdlobjDict, "mdlObject");

  // Create instance to hold result
  //$result = PyObject_CallObject(mdlobjClass, pArgs);

  set_next = PyString_FromString("set_next");
  set_parent = PyString_FromString("set_parent");
  set_first_child = PyString_FromString("set_first_child");
  set_last_child = PyString_FromString("set_last_child");
  set_object_type = PyString_FromString("set_object_type");
  set_vertices = PyString_FromString("set_vertices");
  set_faces = PyString_FromString("set_faces");
  set_regions = PyString_FromString("set_regions");
  set_viz_value = PyString_FromString("set_viz_value");

//  for (objp=r_objp->first_child; objp!=NULL ; objp=objp->next) {
  objp = r_objp;
  p_objp = NULL;
  prev_sib = NULL;
  p_mdlobj = NULL;
  while (objp!=NULL) {
    // Build argument list
    arg = PyString_FromString(objp->name);
    pArgs = PyTuple_New(1);
    PyTuple_SetItem(pArgs, 0, arg);
    // Create instance of python mdl object
    mdlobj = PyObject_CallObject(mdlobjClass, pArgs);

    if (objp->object_type == META_OBJ) {
      // meta object
      o = PyInt_FromLong(META_OBJ);
      PyObject_CallMethodObjArgs(mdlobj,set_object_type,o,NULL);

      if (objp == r_objp) {
        // this is the root meta object so set $result to root meta object
        $result = mdlobj;
      }
      else {
        // set parent of this meta object
        PyObject_CallMethodObjArgs(mdlobj,set_parent,p_mdlobj,NULL);

        // set first child of parent
        if (objp == p_objp->first_child) {
          PyObject_CallMethodObjArgs(p_mdlobj,set_first_child,mdlobj,NULL);
        }
        // set last child of parent
        if (objp == p_objp->last_child) {
          PyObject_CallMethodObjArgs(p_mdlobj,set_last_child,mdlobj,NULL);
        }

        // calculate intermediate t-form matrix of meta object
        mult_matrix(p_objp->t_matrix,objp->t_matrix,objp->t_matrix,4,4,4);
      }

      // set next of previous sibling to this object
      if (prev_sib != NULL) {
        PyObject_CallMethodObjArgs(prev_sib,set_next,mdlobj,NULL);
      }


      // advance to first child of this meta object
      prev_sib = NULL;
      p_mdlobj = mdlobj;
      p_objp = objp;
      objp = objp->first_child;
    }
    else {
      // polygon list object
      o = PyInt_FromLong(POLY_OBJ);
      PyObject_CallMethodObjArgs(mdlobj,set_object_type,o,NULL);

      // set parent of this object
      PyObject_CallMethodObjArgs(mdlobj,set_parent,p_mdlobj,NULL);

      // set first child of parent
      if (objp == p_objp->first_child) {
        PyObject_CallMethodObjArgs(p_mdlobj,set_first_child,mdlobj,NULL);
      }
      // set last child of parent
      if (objp == p_objp->last_child) {
        PyObject_CallMethodObjArgs(p_mdlobj,set_last_child,mdlobj,NULL);
      }

      // set next of previous sibling to this object
      if (prev_sib != NULL) {
        PyObject_CallMethodObjArgs(prev_sib,set_next,mdlobj,NULL);
      }

      // calculate final t-form matrix of object
      mult_matrix(p_objp->t_matrix,objp->t_matrix,objp->t_matrix,4,4,4);

      // set vertices, faces, and regions of polygon list object
      n_verts = objp->n_verts;
      PyObject *vertices = PyList_New(n_verts);
      for (i = 0; i < n_verts; i++) {
        v = PyTuple_New(3);

        p[0][0] = objp->vertices[i]->vertex->x;
        p[0][1] = objp->vertices[i]->vertex->y;
        p[0][2] = objp->vertices[i]->vertex->z;
        p[0][3] = 1.0;
        mult_matrix(p,objp->t_matrix,p,1,4,4);
        objp->vertices[i]->vertex->x = p[0][0];
        objp->vertices[i]->vertex->y = p[0][1];
        objp->vertices[i]->vertex->z = p[0][2];
        
        o = PyFloat_FromDouble(objp->vertices[i]->vertex->x);
        PyTuple_SetItem(v,0,o);
        o = PyFloat_FromDouble(objp->vertices[i]->vertex->y);
        PyTuple_SetItem(v,1,o);
        o = PyFloat_FromDouble(objp->vertices[i]->vertex->z);
        PyTuple_SetItem(v,2,o);

        PyList_SetItem(vertices,i,v);
      }

      n_faces = objp->n_faces;
      PyObject *faces = PyList_New(n_faces);
      for (i = 0; i < n_faces; i++) {
        f = PyTuple_New(objp->faces[i]->polygon->n_verts);

        for (j = 0; j < objp->faces[i]->polygon->n_verts; j++) {
          o = PyInt_FromLong(objp->faces[i]->polygon->vertex_index[j]);
          PyTuple_SetItem(f,j,o);
        }

        PyList_SetItem(faces,i,f);
      }

      region_dict = NULL;
      if (objp->regions!=NULL) {
        region_dict = PyDict_New();
        for (rlp=objp->regions; rlp!=NULL; rlp=rlp->next) {
          objregClass = PyDict_GetItemString(mdlobjDict, "objRegion");

          // Build argument list
          reg_name = PyString_FromString(rlp->name);
          pArgs = PyTuple_New(1);
          PyTuple_SetItem(pArgs, 0, reg_name);

          // Create instance to hold this region
          reg = PyObject_CallObject(objregClass, pArgs);

          n_elements = rlp->n_elements;
          reg_elements = PyTuple_New(n_elements);
          for (i = 0; i < n_elements; i++) {
            o = PyInt_FromLong(rlp->elements[i]);
            PyTuple_SetItem(reg_elements,i,o);
          }

          PyObject_CallMethodObjArgs(reg,set_faces,reg_elements,NULL);
    
          viz_value = PyInt_FromLong(rlp->viz_value);
          PyObject_CallMethodObjArgs(reg,set_viz_value,viz_value,NULL);

          PyDict_SetItem(region_dict,reg_name,reg);

        }
      }

      PyObject_CallMethodObjArgs(mdlobj,set_vertices,vertices,NULL);
      PyObject_CallMethodObjArgs(mdlobj,set_faces,faces,NULL);

      if (objp->regions!=NULL) {
        PyObject_CallMethodObjArgs(mdlobj,set_regions,region_dict,NULL);
      }

      // advance to next sibling of this object
      prev_sib = mdlobj;
      objp = objp->next;
      if (objp == NULL) {
        // advance to next sibling of parent object
        prev_sib = p_mdlobj;
        objp=p_objp->next; 
      }
    }
  }
}

struct object *mdl_parser(char *filename);
