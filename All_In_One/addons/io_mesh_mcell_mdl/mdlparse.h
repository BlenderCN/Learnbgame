#ifndef MDLPARSE_H
#define MDLPARSE_H

#include <sys/types.h>

struct element_list {
  struct element_list *next;
  u_int begin;
  u_int end;
};

int mdlparse(void);
int mdlerror(char *str);

#endif
