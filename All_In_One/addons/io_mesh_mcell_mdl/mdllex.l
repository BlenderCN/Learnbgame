%{
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include "mdlparse.h"
#include "mdlparse.bison.h"

extern int line_num;
extern char *cval,*cval_2,*strval;
extern int ival;
extern double rval;
extern char err_msg[128];
char *my_strdup(char *s);

%}

/* Set up function name prefixes and output file name */
%option prefix="mdl"
%option outfile="mdllex.flex.c"

/* Disable yywrap feature */
%option noyywrap

/* Eliminate unused symbols to eliminate compiler warnings */
%option nounput
%option noyy_top_state

%p 10000
%a 10000 
%o 10000
%e 2000
%n 1000

R ([-]*[0-9]+\.)|([-]*[0-9]*\.[0-9]+)|([-]*[0-9]+[eE][+-]?[0-9]+)|([-]*[0-9]+\.[0-9]*[eE][+-]?[0-9]+)|([-]*[0-9]*\.[0-9]+[eE][+-]?[0-9]+)
I ([-]*[0-9]+)
N ({R}|{I})
IDENT [A-Za-z][A-Za-z0-9\_\.]*

%%

[ \t]+			;
^"#"[^\n]*$		;
"OBJECT"		{return(OBJECT);}
"POLYGON_LIST"		{return(POLYGON_LIST);}
"VERTEX_LIST"		{return(VERTEX_LIST);}
"ELEMENT_CONNECTIONS"	{return(ELEMENT_CONNECTIONS);}
"DEFINE_SURFACE_REGIONS"	{return(DEFINE_SURFACE_REGIONS);}
"ELEMENT_LIST"	        {return(INCLUDE_ELEMENTS);}
"ALL_ELEMENTS"	        {return(ALL_ELEMENTS);}
"MOLECULE_DENSITY"      {return(MOLECULE_DENSITY);}
"MOLECULE_NUMBER"       {return(MOLECULE_NUMBER);}
"SURFACE_CLASS"         {return(SURFACE_CLASS);}
"VIZ_VALUE"	        {return(VIZ_VALUE);}
"SCALE"	                {return(SCALE);}
"ROTATE"	        {return(ROTATE);}
"TRANSLATE"	        {return(TRANSLATE);}
"EXP"                   {return(EXP);}
"LOG"                   {return(LOG);}
"LOG10"                 {return(LOG10);}
"MAX"                   {return(MAX_TOK);}
"MIN"                   {return(MIN_TOK);}
"ROUND_OFF"             {return(ROUND_OFF);}
"FLOOR"                 {return(FLOOR);}
"CEIL"                  {return(CEIL);}
"SIN"                   {return(SIN);}
"COS"                   {return(COS);}
"TAN"                   {return(TAN);}
"ASIN"                  {return(ASIN);}
"ACOS"                  {return(ACOS);}
"ATAN"                  {return(ATAN);}
"SQRT"                  {return(SQRT);}
"ABS"                   {return(ABS);}
"MOD"                   {return(MOD);}
"PI"                    {return(PI_TOK);}
"RAND_UNIFORM"          {return(RAND_UNIFORM);}
"RAND_GAUSSIAN"         {return(RAND_GAUSSIAN);}
"SEED"                  {return(SEED);}
"STRING_TO_NUM"         {return(STRING_TO_NUM);}
{R}                     {sscanf((const char *)mdltext,"%lf",&rval); return(REAL);}
{I}                     {sscanf((const char *)mdltext,"%d",&ival); return(INTEGER);}
{IDENT}                 {
                           if (cval==NULL) {
                             cval_2=NULL;
                             cval=strdup(mdltext);
                           }
                           else {
                             cval_2=cval;
                             cval=strdup(mdltext);
                           }
                           if(cval == NULL){
                                fprintf(stderr,"File '%s', Line %ld: Out of memory while parsing variable name: %s\n", __FILE__, (long)__LINE__, mdltext);
                                exit(1);
                           }

                           return(VAR);
                        }
\"(([^\"]*)|((\\\")*))*\"  {
                             strval = strdup(mdltext);
                             return (STR_VALUE);
                           }
[\'\,\(\)\/\-\+\=\^\[\]\{\}\|\<\>\*\#\~\@\:\&\;] {return(mdltext[0]);}
.			;
\n			{line_num++;}
