#include <stdio.h>
#include <glib.h>

#include "touchatag_reader.h"
#include "touchatag_taglist.h"
#include "touchatag_time.h"

int main() {
	
	int numofdev, i;
	libusb_t *libusb;
	reader_t *reader;
	
	libusb = g_new0 (libusb_t, 1);

	printf ("\n ****************\n");
	printf (" main_reader_info\n");
	printf (" ****************\n\n");
	
	printf (" detect all the readers and print info using lib-touchatag-1.0\n\n");
	
	if ((numofdev = touchatag_scan_bus (libusb)) != 0) {
		
		reader = g_new0 (reader_t, numofdev);

		/* Turn on all the readers connected and send INIT commands */
		touchatag_reader_init_all (libusb, reader);

		/* Get reader IDs */
		touchatag_reader_get_all_reader_id (libusb, reader);
		touchatag_reader_get_all_firmware (libusb, reader);
		touchatag_reader_get_all_reader_sam_code (libusb, reader);
		
		for (i = 0; i < numofdev; i++) {
			printf (" Reader %d\n", i);
			printf (" Reader ID:                      %s\n", (char *) touchatag_reader_return_reader_id (&reader[i]));
			printf (" Reader FIRMWARE:                %s\n", (char *) touchatag_reader_return_reader_firmware (&reader[i]));
			printf (" Reader SAM SERIAL CODE:         %s\n", (char *) touchatag_reader_return_reader_serial_sam (&reader[i]));
			printf (" Reader SAM IDENTIFICATION CODE: %s\n\n", (char *) touchatag_reader_return_reader_identification_sam (&reader[i]));
		}
	}

	touchatag_reader_power_off_all (libusb, reader);
	
return 0;
}
