#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "mdlparse.h"
#include "mdlmesh_parser.h"

extern FILE *mdlin;
char *curr_file;
int line_num;
struct object *root_objp;

struct object *mdl_parser(char *filename)
{


  line_num = 0;
  root_objp = NULL;
  curr_file = filename;
  mdlin = NULL;

	if ((mdlin=fopen(filename,"r"))==NULL) {
	  fprintf(stderr,"mdlmesh_parser: error opening file: %s\n",filename);
	  fflush(stdout);
	  return(NULL);
	} 

	if (mdlparse()) {
	  fprintf(stderr,"mdlmesh_parser: error parsing file: %s\n",filename);
	  return(NULL);
	} 
	fclose(mdlin);

	return(root_objp);
}
