from libcpp cimport bool
from libc.stdio cimport FILE

cdef extern from "stdio.h":
    cdef FILE* fopen(char* path, char* mode)
    cdef int fclose(FILE*)

cdef extern from "voro/src/voro++.hh" namespace "voro":
    cdef cppclass container:
        container(double xmin, double xmax, double ymin, double ymax, double zmin, double zmax,
                    int nx, int ny, int nz, bool xp, bool yp, bool zp, int p)
        void put(int i, double x, double y, double z)
        void print_custom(char *format, FILE *fp)
        void add_wall(wall_plane* w)
        bool point_inside(double x, double y, double z)

    cdef cppclass wall_plane:
        wall_plane(double xn, double yn, double zn, double dn, int w_id)

cdef class domain:
    cdef container *thisptr

    def __cinit__(self, double xmin, double xmax, double ymin, double ymax, double zmin, double zmax, \
    int nx, int ny, int nz, bool xp, bool yp, bool zp, int p):
        self.thisptr = new container(xmin, xmax, ymin, ymax, zmin, zmax, nx, ny,
                    nz, xp, yp, zp, p)

    def __dealloc__(self):
        del self.thisptr

    def put(self, i, x, y, z):
        self.thisptr.put(i, x, y, z)

    def print_custom(self, format, fp):
        fpc = fp.encode('UTF-8')
        r = "w+".encode('UTF-8')
        cdef char* path = fpc
        cdef char* mode = r
        cdef FILE* fil = fopen(path, mode)

        if (fil == NULL):
            print("Couldnt open file!", fp)
            return

        f = format.encode('UTF-8')
        cdef char * formatstr = f
        self.thisptr.print_custom(formatstr, fil)
        cdef int ret = fclose(fil)
      
        if (ret != 0):
            print("Closing file error!", fp)

    def add_wall(self, l):
        cdef wall_plane* wp = NULL
        for e in l:                      
            wp = new wall_plane(e[0], e[1], e[2], e[3], e[4])
            self.thisptr.add_wall(wp)

    def point_inside(self, x, y, z):
        return self.thisptr.point_inside(x, y, z)



