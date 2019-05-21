MAKESDNA_IPATH=/home/rdb/local/src/blender/source/blender/makesdna/

all: bpb.so
bpb.so: bpb_api.h intern/*.cxx intern/*.h intern/*.I
	panc++ -shared -o bpb.so -O1 -ggdb -fPIC intern/bpb_composite.cxx -I. -I$(MAKESDNA_IPATH)
clean:
	rm -f bpb.so
.PHONY: all clean
