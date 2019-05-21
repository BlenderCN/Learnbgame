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

	printf ("\n *****************\n");
	printf (" main_reader_blink\n");
	printf (" *****************\n\n");
	
	printf (" detect all the readers and make the leds blink using lib-touchatag-1.0\n\n");
	
	if ((numofdev = touchatag_scan_bus (libusb)) != 0) {
		
		reader = g_new0 (reader_t, numofdev);

		/* Turn on all the readers connected and send INIT commands */
		touchatag_reader_init_all (libusb, reader);

		/* Get reader IDs */
		touchatag_reader_get_all_reader_id (libusb, reader);
		
		for (i = 0; i < numofdev; i++)
			printf (" Reader ID: %s\n", (char *) touchatag_reader_return_reader_id (&reader[i]));
			
			printf ("\n Blinking red...\n");
			touchatag_reader_led_blink_set ('r', 0x01, 0x05, 0x01);
			touchatag_reader_led_blink_all_readers (libusb, reader);

			printf (" Blinking orange...\n");
			touchatag_reader_led_blink_set ('o', 0x01, 0x05, 0x01);
			touchatag_reader_led_blink_all_readers (libusb, reader);

			printf (" Blinking green...\n");
			touchatag_reader_led_blink_set ('g', 0x01, 0x05, 0x01);
			touchatag_reader_led_blink_all_readers (libusb, reader);


	}
	printf ("\n");
	touchatag_reader_power_off_all (libusb, reader);
	
return 0;
}
