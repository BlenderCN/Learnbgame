#ifndef LIBUSB_H_
#define LIBUSB_H_

#include <usb.h>

#define MAX_DEV_NUMBER 10

/* 
 \struct Struct containing libusb's attributes 
*/
struct libusb_s{
	int dev_number;
	struct usb_bus *busses;
	struct usb_device *devices [MAX_DEV_NUMBER];
	struct usb_dev_handle *handlers [MAX_DEV_NUMBER];
	
};

typedef struct libusb_s libusb_t;

void libusb_search (libusb_t *libusb, int idVendor, int idProduct);

int libusb_open_all (libusb_t *libusb);

int libusb_close_all (libusb_t *libusb);

#endif /*LIBUSB_H_*/
