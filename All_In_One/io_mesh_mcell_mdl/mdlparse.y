%{

#include <stdlib.h>
#include <stdio.h> 
#include <string.h> 
#include <math.h>
#include "vector.h"
#include "mdlmesh_parser.h"
#include "mdlparse.h"
#include "mdlparse.bison.h"

#include "mdllex.flex.c"

extern FILE *mdlin;
extern int line_num;
extern char *curr_file;
extern struct object *root_objp;

int ival;
double rval;
char *cval,*cval_2,*strval;
struct object *objp,*p_objp;
struct polygon_list *plp,*polygon_head,*polygon_tail,**polygon_array;
struct polygon *pop;
struct vertex_list *vlp,*vertex_head,*vertex_tail,**vertex_array;
struct region_list *region_head,*region_tail,*rlp;
struct vector3 *vecp;
struct vector3 tmp_vec;
struct element_list *element_list_head, *elmlp;
double tmp_mat[4][4];
int vertex_id;
int vertex_count;
int polygon_count;
double x,y,z;
int vert_1,vert_2,vert_3,vert_4;
int i,j;


%}

%name-prefix="mdl"
%output="mdlparse.bison.c"

%union {
int tok;
char *str;
double dbl;
struct vector3 *vec;
} 

%token <tok> REAL INTEGER
%token <tok> OBJECT POLYGON_LIST VERTEX_LIST ELEMENT_CONNECTIONS
%token <tok> DEFINE_SURFACE_REGIONS ELEMENT_LIST VIZ_VALUE
%token <tok> MOLECULE_DENSITY MOLECULE_NUMBER SURFACE_CLASS
%token <tok> INCLUDE_ELEMENTS TO ALL_ELEMENTS
%token <tok> SCALE ROTATE TRANSLATE
%token <tok> VAR
%token <tok> EXP
%token <tok> LOG
%token <tok> LOG10
%token <tok> MAX_TOK
%token <tok> MIN_TOK
%token <tok> ROUND_OFF
%token <tok> FLOOR
%token <tok> CEIL
%token <tok> SIN
%token <tok> COS
%token <tok> TAN
%token <tok> ASIN
%token <tok> ACOS
%token <tok> ATAN
%token <tok> SQRT
%token <tok> ABS
%token <tok> MOD
%token <tok> PI_TOK
%token <tok> RAND_UNIFORM
%token <tok> RAND_GAUSSIAN
%token <tok> SEED
%token <tok> STRING_TO_NUM
%token <str> STR_VALUE
%type <tok> side_name
%type <dbl> int_arg num_arg 

/* Operator associativities and precendences */
%right '='
%left '&' ':'
%left '+' '-'
%left '*' '/'
%left '^'
%left UNARYMINUS

%%

mdl_format:
{
  if ((objp=(struct object *)malloc(sizeof(struct object)))==NULL) {
    mdlerror("Cannot store mesh object");
    return(1);
  }
  objp->name = "ROOT";
  objp->object_type = META_OBJ;
  objp->next = NULL;
  objp->parent = NULL;
  objp->first_child = NULL;
  objp->last_child = NULL;

  init_matrix(objp->t_matrix);
  root_objp = objp;
  p_objp = objp;
}
    mdl_stmt_list
{
}
;


mdl_stmt_list:
    mdl_stmt
  | mdl_stmt_list mdl_stmt
;


mdl_stmt:
    physical_object_def
;


physical_object_def: object_def
;


object_def:
    meta_object_def
  | polygon_list_def
;


list_objects:
        object_def
        | list_objects object_def
;


list_opt_object_cmds:
          /* empty */
        | list_opt_object_cmds opt_object_cmd
;


opt_object_cmd: transformation
;


transformation:
        TRANSLATE '=' '[' num_arg ',' num_arg ',' num_arg ']'
{
  tmp_vec.x = $<dbl>4;
  tmp_vec.y = $<dbl>6;
  tmp_vec.z = $<dbl>8;
  init_matrix(tmp_mat);
  translate_matrix(tmp_mat,tmp_mat,&tmp_vec);
  mult_matrix(objp->t_matrix,tmp_mat,objp->t_matrix,4,4,4);
}
        | SCALE '=' '[' num_arg ',' num_arg ',' num_arg ']'
{
  tmp_vec.x = $<dbl>4;
  tmp_vec.y = $<dbl>6;
  tmp_vec.z = $<dbl>8;
  init_matrix(tmp_mat);
  scale_matrix(tmp_mat,tmp_mat,&tmp_vec);
  mult_matrix(objp->t_matrix,tmp_mat,objp->t_matrix,4,4,4);
}
        | ROTATE '=' '[' num_arg ',' num_arg ',' num_arg ']' ',' num_arg
{
  tmp_vec.x = $<dbl>4;
  tmp_vec.y = $<dbl>6;
  tmp_vec.z = $<dbl>8;
  init_matrix(tmp_mat);
  rotate_matrix(tmp_mat,tmp_mat,&tmp_vec,$<dbl>11);
  mult_matrix(objp->t_matrix,tmp_mat,objp->t_matrix,4,4,4);
};


meta_object_def: VAR OBJECT '{'
{
  if ((objp=(struct object *)malloc(sizeof(struct object)))==NULL) {
    mdlerror("Cannot store mesh object");
    return(1);
  }
  if (cval_2!=NULL)
  {
    objp->name=cval_2;
    cval_2=NULL;
  }
  else
  {
    objp->name=cval;
    cval=NULL;
  }
  objp->object_type = META_OBJ;
  objp->parent = p_objp;
  objp->next = NULL;
  objp->first_child = NULL;
  objp->last_child = NULL;
  init_matrix(objp->t_matrix);

  if (p_objp->first_child == NULL) {
    p_objp->first_child = objp;
    p_objp->last_child = objp;
  }
  else {
    p_objp->last_child->next = objp;
    p_objp->last_child = objp;
  }

  p_objp = objp;
}
        list_objects
{
  objp = p_objp;
}
        list_opt_object_cmds
        '}'
{
  p_objp = p_objp->parent;
};


polygon_list_def: VAR POLYGON_LIST '{'
{
  if ((objp=(struct object *)malloc(sizeof(struct object)))==NULL) {
    mdlerror("Cannot store mesh object");
    return(1);
  }
  if (cval_2!=NULL)
  {
    objp->name=cval_2;
    cval_2=NULL;
  }
  else
  {
    objp->name=cval;
    cval=NULL;
  }
  objp->object_type = POLY_OBJ;
  objp->parent = p_objp;
  objp->next = NULL;
  objp->first_child = NULL;
  objp->last_child = NULL;
  init_matrix(objp->t_matrix);

  if (p_objp->first_child == NULL) {
    p_objp->first_child = objp;
    p_objp->last_child = objp;
  }
  else {
    p_objp->last_child->next = objp;
    p_objp->last_child = objp;
  }

  vertex_count=0;
  polygon_count=0;
  vlp=NULL;
  vertex_head=NULL;
  vertex_tail=NULL;
  plp=NULL;
  polygon_head=NULL;
  polygon_tail=NULL;
  rlp=NULL;
  region_head=NULL;
  region_tail=NULL;
}
	vertex_list_cmd
{ 
  if ((vertex_array=(struct vertex_list **)malloc
       (vertex_count*sizeof(struct vertex_list *)))==NULL) {
    mdlerror("Cannot store vertex array");
    return(1);
  }
  vlp=vertex_head;
  while (vlp!=NULL) {
    vertex_array[vlp->vertex_id]=vlp;
    vlp=vlp->next;
  }
}
	element_connection_cmd
{ 
  if ((polygon_array=(struct polygon_list **)malloc
       (polygon_count*sizeof(struct polygon_list *)))==NULL) {
    mdlerror("Cannot store vertex array");
    return(1);
  }
  plp=polygon_head;
  while (plp!=NULL) {
    polygon_array[plp->polygon_index]=plp;
    plp=plp->next;
  }
  objp->n_verts=vertex_count;
  objp->n_faces=polygon_count;
  objp->vertices = vertex_array;
  objp->faces = polygon_array;
}
	list_opt_polygon_object_cmds
{
  objp->regions = region_head;
}
        list_opt_object_cmds
	'}'
;


vertex_list_cmd: VERTEX_LIST '{'
	list_points
	'}'
;


list_points: point
	| list_points point
;


point: '[' num_arg ',' num_arg ',' num_arg ']'
{
  if ((vecp=(struct vector3 *)malloc(sizeof(struct vector3)))==NULL) {
    mdlerror("Cannot store normal vector");
    return(1);
  }
  vecp->x=$<dbl>2;
  vecp->y=$<dbl>4;
  vecp->z=$<dbl>6;
  if ((vlp=(struct vertex_list *)malloc(sizeof(struct vertex_list)))==NULL) {
    mdlerror("Cannot store vertex list");
    return(1);
  }
  vlp->vertex_id=vertex_count;
  vlp->vertex_index=vertex_count++;
  vlp->vertex=vecp;
  vlp->normal=NULL;
  if (vertex_tail==NULL) {
    vertex_tail=vlp;
  }
  vertex_tail->next=vlp;
  vlp->next=NULL;
  vertex_tail=vlp;
  if (vertex_head==NULL) {
    vertex_head=vlp;
  }
};


element_connection_cmd: ELEMENT_CONNECTIONS '{'
	list_faces
	'}'
;


list_faces: face
	| list_faces face
;


face: '[' int_arg ',' int_arg ',' int_arg ']'
{
  vert_1=$<dbl>2;
  vert_2=$<dbl>4;
  vert_3=$<dbl>6;
  if ((pop=(struct polygon *)malloc(sizeof(struct polygon)))==NULL) {
    mdlerror("Cannot store polygon");
    return(1);
  }
  if ((plp=(struct polygon_list *)malloc(sizeof(struct polygon_list)))==NULL) {
    mdlerror("Cannot store polygon list");
    return(1);
  }
  plp->polygon_id=polygon_count;
  plp->polygon_index=polygon_count++;
  pop->n_verts=3;
  pop->vertex_index[0]=vertex_array[vert_1]->vertex_index;
  pop->vertex_index[1]=vertex_array[vert_2]->vertex_index;
  pop->vertex_index[2]=vertex_array[vert_3]->vertex_index;
  plp->polygon=pop;
  if (polygon_tail==NULL) {
    polygon_tail=plp;
  }
  polygon_tail->next=plp;
  plp->next=NULL;
  polygon_tail=plp;
  if (polygon_head==NULL) {
    polygon_head=plp;
  }
};


list_opt_polygon_object_cmds: /* empty */
	| list_opt_polygon_object_cmds opt_polygon_object_cmd
;


opt_polygon_object_cmd:
	in_obj_define_surface_regions
;


in_obj_define_surface_regions: DEFINE_SURFACE_REGIONS '{'
	list_in_obj_surface_region_defs
	'}'
;


list_in_obj_surface_region_defs: in_obj_surface_region_def
	| list_in_obj_surface_region_defs in_obj_surface_region_def
;


in_obj_surface_region_def: VAR '{'
{
  if ((rlp=(struct region_list *)malloc(sizeof(struct region_list)))==NULL) {
    mdlerror("Cannot store mesh object");
    return(1);
  }
  if (cval_2!=NULL)
  {
    rlp->name=cval_2;
    cval_2=NULL;
  }
  else
  {
    rlp->name=cval;
    cval=NULL;
  }
  rlp->n_elements = 0;
  rlp->elements=NULL;
  element_list_head = NULL;
  rlp->viz_value=0;
  if (region_tail==NULL) {
    region_tail=rlp;
  }
  region_tail->next=rlp;
  rlp->next=NULL;
  region_tail=rlp;
  if (region_head==NULL) {
    region_head=rlp;
  }
}
	element_specifier_list
	list_opt_surface_region_stmts
	'}'
{
  if (rlp->n_elements>0) {
    if ((rlp->elements=(int *)malloc
               (rlp->n_elements*sizeof(int)))==NULL) {
      mdlerror("Out of memory while creating region element list");
      return(1);
    }
    i=0;
    for (elmlp=element_list_head; elmlp!=NULL; elmlp=elmlp->next) {
       for (j = elmlp->begin; j<=elmlp->end; j++) {
        rlp->elements[i]=j;
        i++;
       }
    }
  }
};


element_specifier_list: element_specifier
        | element_specifier_list ',' element_specifier
;


element_specifier:
	incl_element_list_stmt
;


incl_element_list_stmt:  INCLUDE_ELEMENTS '=' '[' list_element_specs ']'
;


list_element_specs: element_spec
	| list_element_specs ',' element_spec
;


element_spec: num_arg
{
  if ((elmlp=(struct element_list *)malloc
             (sizeof(struct element_list)))==NULL) {
    mdlerror("Out of memory while creating element list item");
    return(1);
  }
  elmlp->begin=(unsigned int) ($<dbl>1);
  elmlp->end=elmlp->begin;
  rlp->n_elements++;
  elmlp->next=element_list_head;
  element_list_head=elmlp;
}
	| num_arg TO num_arg
{
  if ((elmlp=(struct element_list *)malloc
             (sizeof(struct element_list)))==NULL) {
    mdlerror("Out of memory while creating element list item");
    return(1);
  }
  elmlp->begin=(unsigned int) ($<dbl>1);
  elmlp->end=(unsigned int) ($<dbl>3);
  rlp->n_elements=elmlp->end-elmlp->begin+1;
  elmlp->next=element_list_head;
  element_list_head=elmlp;
}
	| side_name
{
  if ((elmlp=(struct element_list *)malloc
             (sizeof(struct element_list)))==NULL) {
    mdlerror("Out of memory while creating element list item");
    return(1);
  }
  elmlp->next=element_list_head;
  element_list_head=elmlp;

  if ($<tok>1==ALL_SIDES) {
    elmlp->begin=0;
    elmlp->end=objp->n_faces-1;
    rlp->n_elements=elmlp->end-elmlp->begin+1;
  }
};


side_name:  ALL_ELEMENTS
{
  $$ = ALL_SIDES;
};


list_opt_surface_region_stmts: /* empty */
	| list_opt_surface_region_stmts opt_surface_region_stmt
;


opt_surface_region_stmt:
	  set_surface_class_stmt
	| surface_mol_stmt
	| surface_region_viz_value_stmt
;


set_surface_class_stmt:
          SURFACE_CLASS '=' VAR
{
  if (cval_2!=NULL)
  {
    cval_2=NULL;
  }
  else
  {
    cval=NULL;
  }
}
;


surface_mol_stmt:
         MOLECULE_DENSITY
         '{'
            list_surface_mol_quant
         '}'
        | MOLECULE_NUMBER
         '{'
            list_surface_mol_quant
         '}'
;


list_surface_mol_quant: 
          surface_mol_quant
        | list_surface_mol_quant surface_mol_quant
;


surface_mol_quant:
          surface_molecule '=' num_expr
;


surface_molecule:
         VAR orientation_class
{
  if (cval_2!=NULL)
  {
    cval_2=NULL;
  }
  else
  {
    cval=NULL;
  }
};


orientation_class: /* empty */
          | list_orient_marks
          | ';'
;


list_orient_marks:
            head_mark
          | tail_mark
          | list_orient_marks head_mark
          | list_orient_marks tail_mark
;


head_mark: '\''
;


tail_mark: ','
;


surface_region_viz_value_stmt: VIZ_VALUE '=' num_arg
{
  rlp->viz_value = (int) ($<dbl>3);
};


int_arg: INTEGER {$$=(double)ival;}
;


num_arg: INTEGER {$$=(double)ival;}
	| REAL {$$=rval;}
;


num_expr: num_value
        | arith_expr
;


num_value: num_arg
        | VAR
{
  if (cval_2!=NULL)
  {
    cval_2=NULL;
  }
  else
  {
    cval=NULL;
  }
};


arith_expr:
        '(' num_expr ')'
      | EXP '(' num_expr ')'
      | LOG '(' num_expr ')'
      | LOG10 '(' num_expr ')'                       
      | MAX_TOK '(' num_expr ',' num_expr ')'       
      | MIN_TOK '(' num_expr ',' num_expr ')'      
      | ROUND_OFF '(' num_expr ',' num_expr ')'   
      | FLOOR '(' num_expr ')'                   
      | CEIL '(' num_expr ')'                   
      | SIN '(' num_expr ')'                   
      | COS '(' num_expr ')'                  
      | TAN '(' num_expr ')'                 
      | ASIN '(' num_expr ')'               
      | ACOS '(' num_expr ')'              
      | ATAN '(' num_expr ')'             
      | SQRT '(' num_expr ')'            
      | ABS '(' num_expr ')'            
      | MOD '(' num_expr ',' num_expr ')'            
      | PI_TOK                                      
      | RAND_UNIFORM                               
      | RAND_GAUSSIAN                             
      | SEED                                     
      | STRING_TO_NUM '(' str_expr ')'          
      | num_expr '+' num_expr                  
      | num_expr '-' num_expr                 
      | num_expr '*' num_expr                
      | num_expr '/' num_expr               
      | num_expr '^' num_expr              
      | '-' num_expr %prec UNARYMINUS     
      | '+' num_expr %prec UNARYMINUS    
;


str_expr:
        str_value
      | str_expr '&' str_expr
;


str_value: STR_VALUE
;


%%

int mdlerror(char *s)
{
	fprintf(stderr,"mdlmesh_parser: error on line: %d of file: %s  %s\n",
	        line_num,curr_file,s);
	fflush(stderr);
	return(1);
}

