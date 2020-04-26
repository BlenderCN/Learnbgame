#include <GL/gl.h>
#include <GL/glu.h>
#include <GL/glut.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

int w, h;
//const
int font; // = (int)GLUT_BITMAP_9_BY_15;

FILE *subprocess_pipe;

typedef struct a_line_struct {
  char *line;
  struct a_line_struct* next;
} a_line;

a_line *line_list = NULL;
a_line *last_line = NULL;

static void resize(int width, int height)
{
  const float ar = (float) width / (float) height;
  w = width;
  h = height;
  glViewport(0, 0, width, height);
  glMatrixMode(GL_PROJECTION);
  glLoadIdentity();
  glFrustum(-ar, ar, -1.0, 1.0, 2.0, 100.0);
  glMatrixMode(GL_MODELVIEW);
  glLoadIdentity() ;
}

void setOrthographicProjection() {
  glMatrixMode(GL_PROJECTION);
  glPushMatrix();
  glLoadIdentity();
  gluOrtho2D(0, w, 0, h);
  glScalef(1, -1, 1);
  glTranslatef(0, -h, 0);
  glMatrixMode(GL_MODELVIEW);
}

void resetPerspectiveProjection() {
  glMatrixMode(GL_PROJECTION);
  glPopMatrix();
  glMatrixMode(GL_MODELVIEW);
}

void renderBitmapString(float x, float y, void *font,const char *string){
  const char *c;
  glRasterPos2f(x, y);
  for (c=string; *c != '\0'; c++) {
      glutBitmapCharacter(font, *c);
  }
}

static void display(void){
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
  glColor3d(0.0, 1.0, 0.0);
  setOrthographicProjection();
  glPushMatrix();
  glLoadIdentity();
  
  GLint vp_params[4];
  glGetIntegerv ( GL_VIEWPORT, vp_params );
  int vp_height = vp_params[3];

  a_line *next = line_list;
  int y = vp_height - 20;
  while (next != NULL) {
    renderBitmapString(10,y,(void *)font,next->line);
    next = next->next;
    y = y - 20;
  }
  glPopMatrix();
  resetPerspectiveProjection();
  glutSwapBuffers();
}

void replace_crs ( char *s ) {
  for (int i=0; i<strlen(s); i++) {
    if (s[i] == '\n') s[i] = ' ';
    if (s[i] == '\r') s[i] = ' ';
  }
}

void update(int value){
  char buffer[1010];
  a_line *new_line;
  if (subprocess_pipe != NULL) {
    char *buf = fgets ( buffer, 1000, subprocess_pipe );
    if (buf != NULL) {
      replace_crs(buf);
      printf ( "Input: %s\n", buf );
      new_line = (a_line *) malloc ( sizeof(a_line) );
      new_line->next = NULL;
      new_line->line = (char *) malloc ( 1+strlen(buf) );
      strcpy ( new_line->line, buf );
      new_line->next = line_list;
      line_list = new_line;
    }
  }
  glutTimerFunc(10, update, 0);
  glutPostRedisplay();
}

int main(int argc, char *argv[])
{
  printf ( "Simulation Control Program ...\n" );

  int command_arg_sep_index = 0;

  int window_x=0;
  int window_y=0;
  
  char *cmd = NULL;

  if (argc > 1) {
    // Search for the first command argument separator
    for (int arg=1; arg<argc; arg++) {
      if ( strcmp ( argv[arg], ":" ) == 0 ) {
        command_arg_sep_index = arg;
        printf ( "Command_arg_sep_index = %d\n", command_arg_sep_index );
        break;
      }
    }
    
    if (command_arg_sep_index >= 1) {
      // Process the application commands before the command argument separator

      for (int arg=1; arg<command_arg_sep_index; arg++) {
        if ( ( strcmp (argv[arg],("?")) == 0 ) || ( strcmp (argv[arg],("/?")) == 0 ) ) {
          printf ( "Args: [?] [x=#] [y=#] [:] [cmd]" );
          printf ( "  x=# - Set the x location of the window" );
          printf ( "  y=# - Set the y location of the window" );
          printf ( "  : - Separates options from command line (needed when both are present)" );
          printf ( "  cmd - Execute the command showing output" );
          exit(0);
        } else if ( strncmp(argv[arg],"x=",2) == 0 ) {
          sscanf ( argv[arg], "x=%d", &window_x );
        } else if ( strncmp(argv[arg],"y=",2) == 0 ) {
          sscanf ( argv[arg], "y=%d", &window_y );
        } else {
          printf ( "Unrecognized argument: %s", argv[arg] );
        }
      }
    }
      
    // Process the remaining arguments as if they are all parts of the command string

    int command_length = 1; // Allow for the null terminator
    for (int i=command_arg_sep_index+1; i<argc; i++) {
      printf ( "Arg %d = %s\n", i, argv[i] );
      command_length += 1 + strlen(argv[i]); // Allow for spaces between arguments
    }

    cmd = (char *) malloc ( command_length + 1 );  // Allow for mistakes!!
    cmd[0] = '\0';
    for (int i=command_arg_sep_index+1; i<argc; i++) {
      strcat ( cmd, argv[i] );
      if (i < (argc-1) ) {
        strcat ( cmd, " " );
      }
    }
    printf ( "Command: %s\n", cmd );
  }

  printf ( "Command: %s\n", cmd );
  
  subprocess_pipe = popen ( cmd, "r" );
  
  free(cmd);

  font=(int)GLUT_BITMAP_9_BY_15;
  glutInit(&argc, argv);
  glutInitWindowSize(640,480);
  glutInitWindowPosition(window_x,window_y);
  glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH);
  glutCreateWindow("Simulation Control");
  glutReshapeFunc(resize);
  glutDisplayFunc(display);
  glutTimerFunc(25, update, 0);
  glutMainLoop();
  return EXIT_SUCCESS;
}
