grammar lsystem;

FLOAT : ( INT | NEG_INT ) ( '.' [0-9]+ )? ;

INT : [1-9][0-9]* | '0';
NEG_INT: '-' [1-9][0-9]*;

SPACE : ' ' | '\t';

NT : [A-Z]([a-z] | [A-Z] | [0-9])*;
DEFINE : '_' NT ;

CONTENT_END : ';' '\n' ? ;
CONTENT_START : SPACE * ':' SPACE * ;
SECTION_START : ':' '\n' ;
ROT : 'r' ;
DRAW : 'd' ;
MOVE : 'm' ;
PUSH : 'push' ;
POP : 'pop' ;

INIT_SECTION : 'init' ;
INIT_START : 'start' ;
DEFINE_SECTION : 'define' ;
RULES_SECTION : 'rules' ;
FINAL_SECTION : 'final' ;

probability : FLOAT ;

rand_entry : FLOAT | '{' SPACE * FLOAT SPACE * ',' SPACE * FLOAT SPACE *  '}' ;

rotation : ROT ( '(' ( ( SPACE * rand_entry SPACE * ',' ) ?  SPACE * rand_entry SPACE * ',' ) ? SPACE * rand_entry SPACE * ')' | rand_entry );
move: MOVE rand_entry ?;
draw: DRAW rand_entry ?;
push: PUSH;
pop: POP;

term : rotation | move | draw | push | pop;
non_term : NT ;
define_term: DEFINE ;

init_sec : ( INIT_SECTION SECTION_START ) ? init_start ;
init_start : INIT_START CONTENT_START non_term CONTENT_END ;

define_sec : DEFINE_SECTION SECTION_START define_entity + ;
define_entity : define_term CONTENT_START define_res CONTENT_END ;
define_res : ( (non_term | term) SPACE + ) * (non_term | term | define_term) SPACE * ;

rule_sec : RULES_SECTION SECTION_START rule_entity + ;
rule_entity : non_term (SPACE +  probability)? CONTENT_START rule_res CONTENT_END ;
rule_res : ( (non_term | term | define_term ) SPACE + ) * (non_term | term | define_term) SPACE * ;

final_sec : FINAL_SECTION SECTION_START final_rule_entity + ;
final_rule_entity : non_term CONTENT_START final_rule_res  CONTENT_END ;
final_rule_res : ( ( term | define_term ) SPACE + ) * ( term | define_term ) SPACE *;

code : init_sec define_sec ? rule_sec final_sec ? EOF;
