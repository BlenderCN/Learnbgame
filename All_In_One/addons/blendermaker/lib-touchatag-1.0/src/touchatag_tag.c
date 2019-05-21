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

#include <string.h>
#include <stdio.h>
#include "touchatag_tag.h"
#include "touchatag_reader.h"


/*
 Prints tag HEX DATA (all the memory)
*/
void
touchatag_tag_print_hex_all_data_mem (tag_t *tag)
{
	int i;
	for (i = 0; i < 64; i++)
 		printf("%02x ",(unsigned char) tag->data[i]);
}


/*
 Returns tag HEX DATA as string (all the memory)
*/
char
*touchatag_tag_return_hex_all_data_mem (tag_t *tag)
{
	char *string;
	char a[10];
	int i, z;

	string = (char *) malloc (64 * 2);
	
	for (i = 0; i < 64; i++) {
		z = sprintf (a, "%02x", tag->data[i]);
		string[2*i] = a[z-2];
		string[2*i+1] = a[z-1];
	}
	string[2*i] = '\0';

	return strdup (string);
}


/*
 Prints tag HEX DATA (only 48 memory bytes)
*/
void
touchatag_tag_print_hex_data_mem (tag_t *tag)
{
	int i;
	for (i = 0; i < 48; i++)
 		printf("%x ",(unsigned char) tag->data[i+16]);
}


/*
 Returns tag HEX DATA as string (only 48 memory bytes)
*/
char
*touchatag_tag_return_hex_data_mem (tag_t *tag)
{
	char *string;
	char a[10];
	int i, z;

	string = (char *) malloc (48 * 2);
	
	for (i = 0; i < 48; i++) {
		z = sprintf (a, "%02x", tag->data[i+16]);
		string[2*i] = a[z-2];
		string[2*i+1] = a[z-1];
	}
	string[2*i] = '\0';

	return strdup (string);
}

/*
 Prints tag ASCII DATA (all the memory)
*/
void
touchatag_tag_print_ascii_all_data_mem (tag_t *tag)
{
	int i;
 	for (i = 0; i < 64; i++)
 		printf("%c ", tag->data[i]);
}


/*
 Prints tag ASCII DATA (only 48 memory bytes)
*/
void
touchatag_tag_print_ascii_data_mem (tag_t *tag)
{
	int i;
 	for (i = 0; i < 48; i++)
 		printf("%c ", tag->data[i+16]);
}


/*
 Returns tag ASCII DATA as string (only 48 memory bytes)
*/
char
*touchatag_tag_return_ascii_data_mem (tag_t *tag)
{
	char *string;
	char a[10];
	int i, z;

	string = (char *) malloc (48 * 2);

	for (i = 0; i < 48; i++) {
		z = sprintf (a, "%c ", tag->data[i+16]);
		string[2*i] = a[z-2];
		string[2*i+1] = a[z-1];
	}
	return strdup (string);
}


/*
 Prints the link written in the touchatag tag
*/
void
touchatag_tag_print_touchatag_link (tag_t *tag)
{
	int i;	
 	for (i = 0; i < 24; i++)
 		printf("%c ", tag->data[i+23]);
}


/*
 Returns the link written in the touchatag tag
*/
char
*touchatag_tag_return_touchatag_link (tag_t *tag)
{
	char *string;
	int i;
	
	string = (char *) malloc (24);

 	for (i = 0; i < 24; i++)
 		string[i] = tag->data[i+23];
	
	return strdup (string);
}


/*
 Prints the tag UID
 */
void
touchatag_tag_print_tag_uid (tag_t *tag)
{
 	int i;
 	for (i=0; i<7; i++)
 		printf("%02X ", (unsigned char) tag->uid[i]);
}


/*
 Returns tag UID (as string)
*/
char
*touchatag_tag_return_tag_uid (tag_t *tag)
{
	char *string;
	char a[10];
	int i, z;

	string = (char *) malloc (UID_TAG_SIZE * 2);

	for (i = 0; i < 7; i++) {
		z = sprintf (a, "%02x", tag->uid[i]);	
		
		string[2*i] = a[z-2];
		string[2*i+1] = a[z-1];
	}
	string[2*i] = '\0';
	return strdup (string);
}


/*
 Prints HEX DATA of tag's OTP memory (page 4)
*/
void
touchatag_tag_print_hex_data_otp (tag_t *tag)
{
	int i;
	for (i = 0; i < 4; i++)
 		printf("%02x ", (unsigned char) tag->data[i+12]);
}


/*
 Prints DATA of the 32 OPT BITS  (page 4)
*/
void
touchatag_tag_print_otps (tag_t *tag)
{
	int i,z,j;
	char a[10];
	char t[] = "ehi!";
	long int lb;
	char lbs[] = "00000000 00000000";
	for (j = 0; j < 2; j++) {	
		for (i = 0; i < 2; i++) {
			z = sprintf (a, "%02x", (unsigned char) tag->data[12+j*2+i]);
			t[2*i] = a[0];
			t[2*i+1] = a[1];
		}	
		lb = strtol (t,NULL,16);
		z = 16;
		for (i = 0; i < 8; i++) {
			if (lb%2 != 0) lbs[z] = '1';
			else lbs[z] = '0';
			lb = lb/2;
			z--;
		}
		z--;
		for (i = 0; i < 8; i++) {
			if (lb%2 != 0) lbs[z] = '1';
			else lbs[z] = '0';
			lb = lb/2;
			z--;
		}
		printf ("%s ",lbs);
	}
}


/*
 Prints HEX LBYTES
*/
void
touchatag_tag_print_hex_lbytes (tag_t *tag)
{
	printf("%x %x", (unsigned char) tag->data[10], (unsigned char) tag->data[11]);
}


/*
 Prints ASCII LBYTES
*/
void
touchatag_tag_print_lbits (tag_t *tag)
{
	int i,z;
	char a[10];
	char t[]="ehi!";
	long int lb;
	char lbs[] = "00000000 00000000";
	
	for (i = 0; i < 2; i++) {
		z= sprintf (a, "%02x", (unsigned char) tag->data[10+i]);
		t[2*i] = a[0];
		t[2*i+1] = a[1];
	}	
	printf ("%s \n",t);
	lb = strtol (t,NULL,16);
	printf ("%ld\n",lb);
	z = 16;
	for (i = 0; i < 8; i++) {
		if (lb%2 != 0) lbs[z] = '1';
		lb = lb/2;
		printf ("ld : %ld \n", lb);
		z--;
	}
	z--;
	for (i = 0; i < 8; i++) {
		if (lb%2 != 0) lbs[z] = '1';
		lb = lb/2;
		printf ("ld : %ld \n", lb);
		z--;
	}
	printf ("%s\n", lbs);
}
