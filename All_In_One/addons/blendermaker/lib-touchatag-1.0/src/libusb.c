/*
 * Copyright © 2010
 * Andrea Costa <nukemup@hotmail.com>
 * Stefano Raimondi Cominesi <stefano.rc@hotmail.it>
 *
 * Licensed under the GNU General Public License Version 2
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>
 * or write to the Free Software Foundation, Inc., 51 Franklin St
 * Fifth Floor, Boston, MA  02110-1301  USA
 */

#include "libusb.h"


void
libusb_search (libusb_t *libusb, int idVendor, int idProduct)
{
	struct usb_bus *bus;
	struct usb_device *dev;

	usb_init();
	usb_find_busses();
	usb_find_devices();

	libusb->busses = usb_get_busses ();
	libusb->dev_number = 0;

	for (bus = libusb->busses; bus; bus = bus->next){
		for (dev = bus->devices; dev; dev = dev->next){
			if ((dev->descriptor.idVendor == idVendor) && (dev->descriptor.idProduct == idProduct)){
				libusb->devices[libusb->dev_number] = dev;
				libusb->dev_number++;	
			}
		}
	}
}


int
libusb_open_all (libusb_t *libusb)
{	
	int i;	
	for (i = 0; i < libusb->dev_number ; i++) {
		if ((libusb->handlers[i] = usb_open (libusb->devices[i])) == NULL)
			return -1;
		
		if (usb_claim_interface(libusb->handlers[i], 0) < 0)
			return -1;
	}
	return 0;
}


int
libusb_close_all (libusb_t *libusb)
{
	int i;
	for ( i=0 ; i < libusb->dev_number ; i++){
		if (usb_close (libusb->handlers[i]) < 0)
			return 0;
	}
	return 0;
}


int
libusb_reset (libusb_t *libusb)
{
	int i;
	for ( i = 0 ; i < libusb->dev_number ; i++){
		if (usb_reset (libusb->handlers[i]) < 0)
			return -1;
	}
	return 0;
}			

