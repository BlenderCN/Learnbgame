/** \file touchatag_tag.h
*   \brief This header file contains every function related with tags and their attributes
*/

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

#ifndef TOUCHATAG_TAG_H_
#define TOUCHATAG_TAG_H_

#define UID_TAG_SIZE 7
#define DATA_TAG_SIZE 64

/* 
 /struct Struct containing tag's attributes
*/
struct tag_s{
	char uid[UID_TAG_SIZE];    ///< Unique tag identification number (7 bytes)
	char data[DATA_TAG_SIZE];  ///< Data bytes (64 bytes)
};

typedef struct tag_s tag_t;

/** \brief Prints tag UID
 * 
 * This function prints the UID of the given tag.
 */
void touchatag_tag_print_tag_uid (tag_t *tag);

/** \brief Prints touchatag tag link
 * 
 * This function prints the link written in the "touchatag tag" memory of the given tag.
 */
void touchatag_tag_print_touchatag_link (tag_t *tag);

/** \brief Prints in hexadecimal characters the values of the two locking bytes
 * 
 * This function prints in hexadecimal characters the values of the two locking bytes of the given tag.
 */
void touchatag_tag_print_hex_lbytes (tag_t *tag);

/** \brief Prints the values of the 16 locking bits
 * 
 * This function prints the values of the 16 locking bits of the given tag.
 */
void touchatag_tag_print_lbits (tag_t *tag);

/** \brief Prints in hexadecimal characters the data in tag's otp memory (page 4)
 * 
 * This function prints in hexadecimal characters the data in tag's otp memory (page 4).
 */
void touchatag_tag_print_hex_data_otp (tag_t *tag);

/** \brief Prints the values of the 32 otp bits  (page 4)
 * 
 * This function prints the values of the 32 otp bits  (page 4).
 */
void touchatag_tag_print_otps (tag_t *tag);

/** \brief Prints in hexadecimal characters the data in tag's Read/Write memory (from page 5 to page 16)
 * 
 * This function prints in hexadecimal characters the data in tag's Read/Write memory (from page 5 to page 16).
 */
void touchatag_tag_print_hex_data_mem (tag_t *tag);

/** \brief Prints in char format the data in tag's Read/Write memory (from page 5 to page 16)
 * 
 * This function prints in char format the data in tag's Read/Write memory (from page 5 to page 16).
 */
void touchatag_tag_print_ascii_data_mem (tag_t *tag);

/** \brief Prints in hexadecimal characters every data in tag's memory
 * 
 * This function prints in hexadecimal characters every data in tag's memory.
 */
void touchatag_tag_print_hex_all_data_mem (tag_t *tag);

/** \brief Prints in char format every data in tag's memory
 * 
 * This function prints in char format every data in tag's memory.
 */
void touchatag_tag_print_ascii_all_data_mem (tag_t *tag);

/** \brief Returns tag UID
 * 
 * This function returns tag UID.
 */
char *touchatag_taglist_return_tag_uid (tag_t *tag);

/** \brief Returns all tag HEX DATA
 * 
 * This function returns all tag HEX DATA.
 */
char *touchatag_tag_return_hex_all_data_mem (tag_t *tag);

/** \brief Returns free tag HEX DATA
 * 
 * This function returns free tag HEX DATA.
 */
char *touchatag_tag_return_hex_data_mem (tag_t *tag);

/** \brief Returns free tag ASCII DATA
 * 
 * This function returns free tag ASCII DATA.
 */
char *touchatag_tag_return_ascii_data_mem (tag_t *tag);

/** \brief Returns touchatag tag link
 * 
 * This function returns the link written in the touchatag tag.
 */
/* Returns the link written in the touchatag tag */
char *touchatag_tag_return_touchatag_link (tag_t *tag);

/** \brief Returns tag UID (as string)
 * 
 * Returns tag UID (as string).
*/
char *touchatag_tag_return_tag_uid (tag_t *tag);

#endif /*TOUCHATAG_TAG_H_*/
