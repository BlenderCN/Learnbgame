
objects = libusb.o touchatag_reader.o touchatag_tag.o touchatag_taglist.o touchatag_time.o

%.o: src/%.c
	gcc -c $< -o $@ -g `pkg-config --cflags glib-2.0` -I/usr/include -lusb -lsqlite3

compile: $(objects)
	gcc $(objects) -o rfid_writer src/rfid_writer.c `pkg-config --cflags glib-2.0` `pkg-config --libs glib-2.0` -I/usr/include -lusb -lsqlite3
	gcc $(objects) -o rfid_reader src/rfid_reader.c `pkg-config --cflags glib-2.0` `pkg-config --libs glib-2.0` -I/usr/include -lusb -lsqlite3




clean:
	rm *.o -fv
