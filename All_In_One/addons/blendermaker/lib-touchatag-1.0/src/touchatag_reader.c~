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

#include "touchatag_reader.h"
#include "touchatag_tag.h"
#include "touchatag_time.h"

#include <stdio.h>
#include <string.h>
 
char touchatag_power_down[]= { 0x63, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };	
char touchatag_power_up[] = { 0x62, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00 };

char touchatag_INIT1[] = { 0x6f, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x14, 0x00, 0x00, 0x08 };
char touchatag_INIT2[] = { 0x6f, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x14, 0x04, 0x00, 0x06 };
char touchatag_INIT3[] = { 0x6f, 0x0b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x00, 0x00, 0x06, 0xD4, 0x32, 0x05, 0x00, 0x00, 0x00 };
char touchatag_INIT4[] = { 0x6f, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xC0, 0x00, 0x00, 0x04 };

char touchatag_firm[] = { 0x6f, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0x00, 0x48, 0x00, 0x00, 0x00 };
char touchatag_poll[] = { 0x6f, 0x0a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0x00, 0x00, 0x00, 0x05, 0xd4, 0x60, 0x01, 0x10, 0x10};
char touchatag_getIDtag[] = {0x6f, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0xc0, 0x00, 0x00, 0x11};

char touchatag_read[] = {0x6f, 0x0a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x00, 0x00, 0x05, 0xD4, 0x40, 0x01, 0x30, 0x00};
char touchatag_readconf[] = {0x6f, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0xc0, 0x00, 0x00, 0x15};

char touchatag_write[] = {0x6f, 0x0e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0x00, 0x00, 0x00, 0x09, 0xd4, 0x40, 0x01, 0xa2, 0x04, 0x00, 0x00, 0x00, 0x00};

char touchatag_write_oviesse[] = {0x6f, 0x0e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0x00, 0x00, 0x00, 0x09, 0xd4, 0x40, 0x01, 0xa2, 0x01, 0x00, 0x00, 0x00, 0x00};

char touchatag_blinking[] = { 0x6f, 0x09, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0x00, 0x40, 0x50, 0x04, 0x05, 0x05, 0x01, 0x01};

char touchatag_IDreader[] = { 0x6f, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x14, 0x04, 0x00, 0x06};
char touchatag_SNsam[] = { 0x6f, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x14, 0x00, 0x00, 0x08};
char touchatag_IDsam[] = { 0x6f, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x14, 0x04, 0x00, 0x06};

int touchatag_seektime = 0;
int touchatag_looprate = 0;
int touchatag_numofreader = -1;


/*                                                             
 Looks for touchatag readers and runs all the usb init
*/
int
touchatag_scan_bus (libusb_t *libusb)
{
	libusb_search (libusb, idVendor, idProduct);
	libusb_open_all (libusb);
	return libusb->dev_number;
}
 

/*                                                             
 Turns on all the readers connected and sends INIT commands
*/
void
touchatag_reader_init_all (libusb_t *libusb, reader_t *reader)
{	
	int target;
	
	for (target = 0; target < libusb->dev_number; target++) {

		if (touchatag_command (libusb, touchatag_power_up, sizeof (touchatag_power_up), &reader[target], sizeof (reader[target].recvbuf), target) < 0 ) {
			printf ("Error Power Up\n");
			exit (EXIT_FAILURE);
		}
		
		if (touchatag_command (libusb, touchatag_INIT1, sizeof (touchatag_INIT1), &reader[target], sizeof (reader[target].recvbuf), target) < 0 ) {
			printf ("Error INIT1\n");
			exit (EXIT_FAILURE);
		}

		if (touchatag_command (libusb, touchatag_INIT2, sizeof (touchatag_INIT2), &reader[target], sizeof (reader[target].recvbuf), target) < 0 ) {
			printf ("Error INIT2\n");
			exit (EXIT_FAILURE);
		}
		
		if (touchatag_command (libusb, touchatag_INIT3, sizeof (touchatag_INIT3), &reader[target], sizeof (reader[target].recvbuf), target) < 0 ) {
			printf ("Error INIT3\n");
			exit (EXIT_FAILURE);
		}			

		if (touchatag_command (libusb, touchatag_INIT4, sizeof (touchatag_INIT4), &reader[target], sizeof (reader[target].recvbuf), target) < 0 ) {
			printf ("Error INIT4\n");
			exit (EXIT_FAILURE);
		}	
	}
}


/*
 Sends commands to the readers
*/
int
touchatag_command (libusb_t *libusb, char *command, int command_len, reader_t *reader, int response_len, int target)
{
	int bytes_sent;
	int bytes_recv;
	
	/* Send command */
	if ((bytes_sent = usb_bulk_write (libusb->handlers[target], 0x02, (char *) command, command_len, 10)) < 0 ){
		if ((bytes_sent = usb_bulk_write (libusb->handlers[target], 0x02, (char *) command, command_len, 10)) < 0 ){
			printf ("Error usb_bulk_write\n");
			return -1;
		}
	}

	/* Receve answear (we wait 2 times for it to arrive)*/
	if ((bytes_recv = usb_bulk_read (libusb->handlers[target], 0x82, (char *) reader->recvbuf, response_len, 2000)) < 0){
		if ((bytes_recv = usb_bulk_read (libusb->handlers[target], 0x82, (char *) reader->recvbuf, response_len, 2000) < 0)){
			printf ("Error usb_bulk_read 2000\n");
			return -1;
		}
	}
	return bytes_recv;
}


/*
 Uses each reader to look for tags (not together!!)
*/
int
touchatag_reader_polling_all_readers (libusb_t *libusb,reader_t *reader, tag_t *tag)
{
	int t = 0;
	int i = 0;
	int target;
	int recvb;

	char one = {0x13};
	char two = {0x21};
	char get1 = {0x11};
	char get2 = {0x21};
	
	while ( t < (touchatag_seektime/(touchatag_looprate + 90))){

		/* Use all readers */
		for (target = 0; target < libusb->dev_number; target++){
				
			if ((recvb = touchatag_command (libusb, touchatag_poll, sizeof (touchatag_poll), &reader[target], sizeof (reader[target].recvbuf), target)) < 0){
					printf("Error touchatag_poll\n");
					return -1;
			}
			
			/* Something found. Find out what's going on... */
			if (reader[target].recvbuf[11] != 5){
				/* One tag found */
				if (reader[target].recvbuf[11] == one){
					/* Get tag UID and tag DATA */
					touchatag_reader_get_tag_uid (libusb, &reader[target], tag, target);
					touchatag_reader_get_all_data (libusb, &reader[target], &tag[0], target);
					return 1;
				}
				/* One tags found */
				if (reader[target].recvbuf[11] == two){
					/* Change touchatag_getIDtag command to get two tag IDs */
					touchatag_getIDtag[14] = get2;
					/* Get tag UIDs | No DATA can be read */
					touchatag_reader_get_tag_uid (libusb, reader, tag, target);
					/* Reset touchatag_getIDtag to get one tag ID */
					touchatag_getIDtag[14] = get1;
					return 2;
				}	
			}		
		}		 	
		t++;
		usleep (touchatag_looprate * 1000);
	}	
	return 0;
}


/*
 Uses a single reader to look for tags. Reader ID required
*/
int
touchatag_reader_polling_target_reader (libusb_t *libusb,reader_t *reader, tag_t *tag, char *ID)
{								
	int t = 0;
	int i = 0;
	int recvb;

	char one = {0x13};
	char two = {0x21};
	char get1 = {0x11};
	char get2 = {0x21};
	
	int target = touchatag_reader_link_id_reader_usb_handler (libusb, reader, ID);
	
	while ( t < (touchatag_seektime/(touchatag_looprate + 90))){
			
		if ((recvb = touchatag_command (libusb, touchatag_poll, sizeof (touchatag_poll), &reader[target], sizeof (reader[target].recvbuf), target)) < 0){
				printf("Error touchatag_poll\n");
				return -1;
		}
		
		/* Something found. Find out what's going on... */
		if (reader[target].recvbuf[11] != 5){
			/* One tag found */
			if (reader[target].recvbuf[11] == one){	
				/* Get tag UID and tag DATA */
				touchatag_reader_get_tag_uid (libusb, &reader[target], tag, target);
				touchatag_reader_get_all_data (libusb, &reader[target], &tag[0], target);
				return 1;
			}
			/* Two tags found */
			if (reader[target].recvbuf[11] == two){	
				/* Change touchatag_getIDtag command to get two tag IDs */
				touchatag_getIDtag[14] = get2;
				/* Get tag UIDs | No DATA can be read */
				touchatag_reader_get_tag_uid (libusb, reader, tag, target);
				/* Reset touchatag_getIDtag to get one tag ID */
				touchatag_getIDtag[14] = get1;
				return 2;				
			}
		}
		t++;
		usleep (touchatag_looprate * 1000);
	}
	return 0;
}


/*
 Sets reader polling time
*/
void
touchatag_reader_set_time (int time, int rate)
{	
	touchatag_seektime = time;
	if (rate < 1000)
		touchatag_looprate = rate;

	if (rate > 1000)
		touchatag_looprate = 1000;
}


/*
 Gets tag UID or UIDs
 touchatag_reader_get_tag_uid () is able to understand how many tags are found (one or two).
 If two tags are found it saves directly both UIDs.
*/
int
touchatag_reader_get_tag_uid (libusb_t *libusb,reader_t *reader, tag_t *tag, int target)
{
	int i, recvb;
	
	if ((recvb = touchatag_command (libusb, touchatag_getIDtag, sizeof (touchatag_getIDtag), reader, sizeof (reader->recvbuf), target)) < 0){
		printf("Error touchatag_getIDtag\n");
		return -1;
	}
	
	/* Save first tag UID */
	for (i = 0; i < 7; i++){
		tag[0].uid[i] = reader->recvbuf[i+20];
	}

	/* Save second tag UID (only if two tags are found) */
	if (reader->recvbuf[29] = 0x02) {
		for (i = 0; i < 7; i++) {
			tag[1].uid[i] = reader->recvbuf[i+34];
		}
	}
}


/*
 Turns off all the readers
*/
void
touchatag_reader_power_off_all (libusb_t *libusb, reader_t *reader)
{
 	int target;
 	int recvb;
 	int i;
 	for (target = 0; target < libusb->dev_number; target++){
		if(recvb = (touchatag_command(libusb, touchatag_power_down, sizeof (touchatag_power_down), reader, sizeof (reader->recvbuf), target)) < 0) {
			printf("Errore power off handler\n");
 		}
	}
 	libusb_close_all (libusb);
}
 
 
/*
 Turns off the target reader
*/
void
touchatag_reader_power_off_target_reader (libusb_t *libusb, reader_t *reader, char *ID)
{
 	int target;
 	int recvb;
 	int i;
	
 	target = touchatag_reader_link_id_reader_usb_handler (libusb, reader, ID);
	
	if(recvb = (touchatag_command (libusb, touchatag_power_down, sizeof (touchatag_power_down), reader, sizeof (reader->recvbuf), target)) < 0) {
		printf("Errore power off handler\n");
	}
	libusb_close_all (libusb);
}


/*
 Gets target reader firmware
*/
int
touchatag_reader_get_target_firmware (libusb_t *libusb,reader_t *reader, char *ID)
{
	int recvb,j,target, i = 0;
	
	target = touchatag_reader_link_id_reader_usb_handler (libusb, reader, ID);
	if ((recvb = touchatag_command (libusb, touchatag_firm, sizeof (touchatag_firm), reader, sizeof (reader->recvbuf), target)) < 0){
		printf("Errore touchatag_firm\n");
		return -1;
	}

	for (j = 0; j < FIRMWARE_SIZE ; j++)
		reader[target].firmware[j] = reader->recvbuf[j + 10];

	return 0;
}


/*
 Gets the firmware of all the readers
*/
void
touchatag_reader_get_all_firmware (libusb_t *libusb,reader_t *reader)
{
	int recvb, j, i;
	for (i = 0; i < libusb->dev_number; i++){
		if ((recvb = touchatag_command (libusb, touchatag_firm, sizeof (touchatag_firm), reader, sizeof (reader->recvbuf), i)) < 0){
			printf ("Error touchatag_firm\n");
			return;
		}
		for (j = 0; j < FIRMWARE_SIZE ; j++)
			reader[i].firmware[j] = reader->recvbuf[j+10];
	}
}


/*
 Prints reader firmware 
*/
void
touchatag_reader_print_firmware (reader_t *reader)
{
	int i;
 	for (i = 0; i < FIRMWARE_SIZE; i++)
 		printf("%c", reader->firmware[i]);
}


/*
 Saves all the tag data in the correct struct
*/
int
touchatag_reader_get_all_data (libusb_t *libusb,reader_t *reader, tag_t *tag, int target)
{
    int i,j;
 	int recvb;
 	char q={0x00};

 	for (i = 0; i < 4; i++) {
		if(recvb =(touchatag_command (libusb, touchatag_read, sizeof (touchatag_read), reader, sizeof (reader->recvbuf), target)) < 0) {
			printf ("Error touchatag_read\n");
			return -1;
		}
			
		if(recvb =(touchatag_command(libusb, touchatag_readconf, sizeof (touchatag_readconf), reader, sizeof (reader->recvbuf), target)) < 0) {
			printf ("Error touchatag_readconf\n");
			return-1;
		}
			
		for (j = 0; j < 16; j++) {
			tag->data[i * 16 + j] = reader->recvbuf[j + 13];
		}
		touchatag_read[19]+=4;
 	}	
	/* Reset touchatag_read command */
  	touchatag_read[19] = q;
}


/*
 Gets reader ID (target number required)
*/
int
touchatag_reader_get_reader_id (libusb_t *libusb, reader_t *reader, int target)
{
	int recvb;
	int i;
		
	if ((recvb = touchatag_command (libusb, touchatag_IDreader, sizeof (touchatag_IDreader), reader, sizeof (reader->recvbuf), target)) < 0){
		printf("Errore touchatag_IDreader\n");
		return -1;
	}

	for (i = 0; i < ID_READER_SIZE; i++){
		reader->IDreader[i] = reader->recvbuf[10 + i];
	}
	reader->IDreader[ID_READER_SIZE] = '\0';
	reader->hand = target;
}


/*
 Gets all reader IDs
*/
void
touchatag_reader_get_all_reader_id (libusb_t *libusb, reader_t *reader)
{
	int i;
	for (i=0; i < libusb->dev_number; i++)
		touchatag_reader_get_reader_id (libusb, &reader[i], i);
}


/*
 Prints reader ID
*/
 void
touchatag_reader_print_reader_id (reader_t *reader)
{
	int i;
 	for (i = 0;i < 6; i++)
 		printf("%c", reader->IDreader[i]);
}


/* 
 Sets reader blinking 
 3 possible colors 'r' 'g' 'o'
 Number of repetition
 Timing on/off
 Un numero elevato di ripetizioni da errore usb_bulk_read -> aumentare il tempo di attesa di risposta in touchatag_command
*/
void
touchatag_reader_led_blink_set (char colour, int repetition, int time1, int time2)
{
	touchatag_blinking[15] = time1;
	touchatag_blinking[16] = time2;
	touchatag_blinking[17] = repetition;

	if ( colour =='r') touchatag_blinking[13] = 0x50;
	if ( colour =='g') touchatag_blinking[13] = 0xa0;
	if ( colour =='o') touchatag_blinking[13] = 0xf0;	
}


/*
 Blinks all the readers
*/
void
touchatag_reader_led_blink_all_readers (libusb_t *libusb, reader_t *reader)
{	
	int target;
	int recvb;
	for (target = 0; target < libusb->dev_number; target++){
		if ((recvb = touchatag_command (libusb, touchatag_blinking, sizeof (touchatag_blinking), reader, sizeof (reader->recvbuf), target)) < 0) {
			printf("Error touchatag_blink_all ()\n");
			exit (EXIT_FAILURE);
		}
	}
}


/*
 Blinks just the target reader (ID required)
*/
void
touchatag_reader_led_blink_target_reader (libusb_t *libusb, reader_t *reader, char *ID)
{	
	int recvb, target;
	target = touchatag_reader_link_id_reader_usb_handler (libusb, reader, ID);
	if ((recvb = touchatag_command (libusb, touchatag_blinking, sizeof (touchatag_blinking), reader, sizeof (reader->recvbuf), target)) < 0){
		printf("Error touchatag_blink ()\n");
		exit (EXIT_FAILURE);
	}
}


/*
 Writes on a touchatag ultralight tag (just the last 4 bytes are free)
*/
int
touchatag_reader_write_touchtag_ultralight (libusb_t *libusb, reader_t *reader, tag_t *tag, char *notes, char *ID)
{	
	int recvb, i;
	int target = touchatag_reader_link_id_reader_usb_handler (libusb, reader, ID);

	touchatag_read [19] = 0x0f;

	if(recvb = (touchatag_command (libusb, touchatag_read, sizeof (touchatag_read), reader, sizeof (reader->recvbuf), target)) < 0) {
		printf ("Error touchatag_read\n");
		return -1;
	}
			
	if(recvb =(touchatag_command (libusb, touchatag_readconf, sizeof (touchatag_readconf), reader, sizeof (reader->recvbuf), target)) < 0) {
		printf ("Error touchatag_readconf\n");
		return -1;
	}
	
	/* Set writing stuff in touchatag_write */
	for (i = 0; i < 4; i++) {
		touchatag_write [20 + i] = notes[i];
		printf ("%x ", (unsigned char) notes[i]);
	}
	printf ("\n");
	
	/* Write in the last block */
	touchatag_write [19] = 0x0f;

	if ((recvb = touchatag_command (libusb, touchatag_write, sizeof (touchatag_write), reader, sizeof (reader->recvbuf), target)) < 0){
		printf ("Error touchatag_write\n");
		return -1;
	}
	touchatag_read[19] = 0x00;
}


/*
 Writes data on Mifire Ultralight Tag
*/
int
touchatag_reader_write_mifare_ultralight (libusb_t *libusb, reader_t *reader, tag_t *tag, notes_t *notes, char *ID)
{
	int recvb;
	int i ,j = 0, b, e;
	notes_t temp;
 	char q = {0x00};
	int target = touchatag_reader_link_id_reader_usb_handler (libusb, reader, ID);
	
 	touchatag_read[19] = 0x04;

 	for (i = 0; i < 3; i++) {
		if(recvb =(touchatag_command (libusb, touchatag_read, sizeof (touchatag_read), reader, sizeof (reader->recvbuf), target)) < 0) {
			printf("Error Read\n");
			return-1;
		}

		if(recvb =(touchatag_command(libusb, touchatag_readconf, sizeof (touchatag_readconf), reader, sizeof (reader->recvbuf), target)) < 0) {
			printf("Error ReadConf\n");
			return -1;
		}

		/* Save tag data in temp */
		for (j = 0; j < 16; j++) {
			temp.note[i*16+j] = reader->recvbuf[j+13];
		}
		touchatag_read[19]+=4;
 	}

	/* Reset touchatag_read command */
  	touchatag_read[19] = 0x00;

	for (i = notes->start *4; i < (notes->size + notes->start * 4); i++)
		temp.note[i] = notes->note[i];

	j = 0;

	/* Each cycle writes a block of 4 bytes */
	for(i = 0x04; i <= 0x0f ; i++){

		/* Set writing block */
		touchatag_write[19] = i;

		/* Set writing data */
		touchatag_write[20] = temp.note [4*j];
		touchatag_write[21] = temp.note [(4*j)+1];
		touchatag_write[22] = temp.note [(4*j)+2];
		touchatag_write[23] = temp.note [(4*j)+3];

		printf ("%x ", (unsigned char) temp.note [4*j]);
		printf ("%x ", (unsigned char) temp.note [(4*j)+1]);
		printf ("%x ", (unsigned char) temp.note [(4*j)+2]);
		printf ("%x ", (unsigned char) temp.note [(4*j)+3]);
		printf ("\n");
		
		j++;

		/* Write command */
		if ((recvb = touchatag_command (libusb, touchatag_write, sizeof (touchatag_write), reader, sizeof (reader->recvbuf), target)) < 0){
			printf("Errore touchatag_write\n");
			return -1;
		}	
	}
}


/*
 Sets the parameters for writing operations
*/
void
touchatag_reader_set_writing_notes (int size, int start, char *note, notes_t *notes)
{
	int i;
	notes->size = size;
	notes->start = start;
	for (i = 0; i < size; i++) {
		notes->note[i + (start * 4)] = *(note + i*sizeof(char));
	}	
}


/*
 Links reader ID and usb handler
*/
int
touchatag_reader_link_id_reader_usb_handler (libusb_t *libusb, reader_t *reader, char *ID)
{
	int i, j, z = 0;
	
	for (i = 0; i < libusb->dev_number; i++) {
		for (j = 0; j < 6; j++) {
			if (reader[i].IDreader[j]== *(ID + j * sizeof(char)))
				z++;
		}
		if (z == 6)
			return i;
		
		z=0;
	}
	return -1;
}


/*
 Gets and saves SAM identification and serial number UID
*/
void
touchatag_reader_get_all_reader_sam_code (libusb_t *libusb,reader_t *reader)
{
	int recvb,j,i;
	for (i = 0; i < libusb->dev_number; i++){
		if ((recvb = touchatag_command (libusb, touchatag_SNsam, sizeof (touchatag_SNsam), reader, sizeof (reader->recvbuf), i)) < 0) {
			printf("Errore touchatag_SNsam\n");
			exit (-1);
		}

		for (j = 0; j < SN_SAM_SIZE ; j++)
			reader[i].SNsam[j] = reader->recvbuf[j+10];

		if ((recvb = touchatag_command (libusb, touchatag_IDsam, sizeof (touchatag_IDsam), reader, sizeof (reader->recvbuf), i)) < 0) {
			printf("Errore touchatag_IDsam\n");
			exit (-1);
		}

		for (j = 0; j < 6 ; j++)
			reader[i].IDsam[j] = reader->recvbuf[j+10];
	}
}			


/*
 Prints reader SAM identification number
*/
void
touchatag_reader_print_reader_identification_sam (reader_t *reader)
{
	int i;
 	for (i = 0;i < 6; i++)
 		printf("%02x ", reader->IDsam[i]);
}		


/*
 Prints reader SAM serial number
*/
void
touchatag_reader_print_reader_serial_sam (reader_t *reader) {
	int i;
 	for (i = 0;i < SN_SAM_SIZE; i++)
 		printf("%02x ", reader->SNsam[i]);
}		


/*
 Returns reader SAM serial number
*/
char 
*touchatag_reader_return_reader_serial_sam (reader_t *reader)
{
	char *string;
	char a[10];
	int i, z;

	string = (char *) malloc (SN_SAM_SIZE * 2);
	
	for (i = 0; i < SN_SAM_SIZE; i++) {
		z = sprintf (a, "%02x", reader->SNsam[i]);
		string[2*i] = a[z-2];
		string[2*i+1] = a[z-1];
	}
	string[2*i] = '\0';

	return strdup (string);
}


/*
 Returns reader SAM identification number
*/
char 
*touchatag_reader_return_reader_identification_sam (reader_t *reader)
{
	char *string;
	char a[10];
	int i, z;

	string = (char *) malloc (ID_SAM_SIZE * 3);
	
	for (i = 0; i < ID_SAM_SIZE; i++) {
		z = sprintf (a, "%02x", reader->IDsam[i]);
		string[2*i] = a[z-2];
		string[2*i+1] = a[z-1];
	}
	string[2*i] = '\0';

	return strdup (string);
}



/*
 Returns reader firmware (in ASCII)
*/
char
*touchatag_reader_return_reader_firmware (reader_t *reader)
{
	char *string;
	string = (char *) malloc (FIRMWARE_SIZE);
	snprintf (string, FIRMWARE_SIZE, "%s", reader->firmware);
	return strdup (string);
}


/*
 Returns reader ID (as string)
*/
char
*touchatag_reader_return_reader_id (reader_t *reader)
{
	char *string;
	string = (char *) malloc (ID_READER_SIZE);
	snprintf (string, ID_READER_SIZE, "%s", reader->IDreader);
	return strdup (string);
}
