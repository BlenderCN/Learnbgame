/** \file touchatag_reader.h
*   \brief This header file contains every function related with readers and their attributes
*/
#ifndef TOUCHATAG_READER_H_
#define TOUCHATAG_READER_H_

#include "libusb.h"
#include "touchatag_tag.h"

#define idVendor 0x072f
#define idProduct 0x90cc

#define FIRMWARE_SIZE 15
#define ID_READER_SIZE 7
#define ID_SAM_SIZE 6
#define SN_SAM_SIZE 8
#define RECV_BUF_SIZE 64
#define NOTE_SIZE 48

/* 
 \struct Struct containing reader's attributes 
*/
struct reader_s {
	int hand;                       ///< Number of handler linked to the reader
	char firmware[FIRMWARE_SIZE];   ///< Reader firmware
	char IDreader[ID_READER_SIZE];  ///< Unique reader identification number (ID)
	char recvbuf[RECV_BUF_SIZE];    ///< Buffer for signal exchange with the tags
	char IDsam[ID_SAM_SIZE];        ///< Unique identification number of the reader SAM card
	char SNsam[SN_SAM_SIZE];        ///< Unique serial number of the reader SAM card
};

/*
 \struct Struct created to simplify writing & reading operations
*/
struct notes_s{
	int size;              ///< Number of bytes needed to write
	int start;             ///< First byte it's needed to write 
	char note[NOTE_SIZE];  ///< Values it's needed to write
};

typedef struct reader_s reader_t;
typedef struct notes_s notes_t;

/** \brief Searches for touchatag readers 
 *
 * This function scans the usb ports to find any linked touchatag devices.
 */ 
int touchatag_scan_bus (libusb_t *libusb);

/** \brief Initializes the connection with the readers
 *
 * It switches on the voltage of the usb ports where a touchatag reader is found,
 * after that the function implements the first signals exchanges with the reader.
 */ 
void touchatag_reader_init_all (libusb_t *libusb, reader_t *reader);

/** \brief This function switches off the voltage. Touchatag readers -> OFF
 *
 * This function switches off the voltage of the usb ports where a reader in connected.
 */ 
void touchatag_reader_power_off_all (libusb_t *libusb, reader_t *reader);

/** \brief Exchanges commands with the reader
 *
 * This is an internal function; it sends the hexadecimal given command to the reader and writes the answer in reader_recvbuf
 */ 
int touchatag_command (libusb_t *libusb, char * command, int command_len, reader_t *reader, int response_len, int target);

/** \brief Commands a polling action on all touchatag readers connected
 *
 * This function Commands a polling action on all touchatag readers connected.
 * If a tag is found, functions touchatag_reader_get_tag_uid and touchatag_reader_get_all_data are used.
 * If two tags are found, it only takes both tags uid.
 * Returns found tag number.
 */
int touchatag_reader_polling_all_readers (libusb_t *libusb, reader_t *reader, tag_t *tag);

/** \brief Commands a polling action on the target touchatag reader
 *
 * This function commands a polling action on the target touchatag reader.
 * If a tag is found, functions touchatag_reader_get_tag_uid and touchatag_reader_get_all_data are used.
 * If two tags are found, it only takes both tags' uid.
 * Returns found tag number
 */
int touchatag_reader_polling_target_reader (libusb_t *libusb,reader_t *reader, tag_t *tag, char *ID);

/** \brief Writes on a touchatag tag's memory (last 4 bytes)
 *
 * This function sends the write command to the reader device.
 * It writes only in the 4 bytes (only the last 4 bytes are unlocked).
 */
int touchatag_reader_write_touchtag_ultralight (libusb_t *libusb, reader_t *reader, tag_t *tag, char *notes, char *ID);

/** \brief Writes on Read/Write tag's memory (only MIFARE ULTRALIGHT are allowed)
 *
 * This function sends the write command to the reader device.
 * The size attribute in notes has to be lower than 49 and the starting byte has to be correct too
 */
int touchatag_reader_write_mifare_ultralight (libusb_t *libusb, reader_t *reader, tag_t *tag, notes_t *notes, char *ID);

/** \brief Gets tag UID and saves it in the given tag structure
 *
 * This function gets tag UID and saves it in the given tag structure.
 * Call it only if a tag is found.
 */
int touchatag_reader_get_tag_uid (libusb_t *libusb, reader_t *reader, tag_t *tag, int target);

/** \brief Gets all reader IDs saves them
 *
 * This function gets all the IDs of the connected readers.
 */
void touchatag_reader_get_all_reader_id (libusb_t *libusb, reader_t *reader);

/** \brief Gets target reader ID and saves it in the given reader structure 
 *
 * This function gets the target reader ID and saves it into the given reader data struct.
 */
int touchatag_reader_get_reader_id (libusb_t *libusb, reader_t *reader, int target);

/** \brief Gets both SAM's identification code and serial number of each reader, saving them in the given reader structure
 *
 * This function gets both SAM's identification code and serial number of each reader, saving them in the given reader structure.
 */
void touchatag_reader_get_all_reader_sam_code (libusb_t *libusb, reader_t *reader);

/** \brief Gets reader firmwares and saves them
 *
 * This function gets all reader FIRMWAREs saving them.
 */
void touchatag_reader_get_all_firmware (libusb_t *libusb, reader_t *reader);

/** \brief Gets reader's firmware and saves it in the given reader structure
 *
 * This function gets reader firmware and saves it in the given reader structure.
 */ 
int touchatag_reader_get_target_firmware (libusb_t *libusb, reader_t *reader, char *ID);

/** \brief Sets polling time
 *
 * This function sets the default polling time of all the readers.
 */ 
void touchatag_reader_set_time (int time, int rate);

/** \brief Gets all tag data
 *
 * This function gets all tag data and saves it in the tag structure.
 */ 
int touchatag_reader_get_all_data (libusb_t *libusb, reader_t *reader, tag_t *tag, int target);

/** \brief Blinks every reader leds
 *
 * This function makes start the blinking operation with the parameters setted with touchatag_reader_led_blink_set.
 * If they aren't setted yet, default settings are used.
 */
void touchatag_reader_led_blink_all_readers (libusb_t *libusb, reader_t *reader);

/** \brief Blinks target reader led
 *
 * This function makes start the blinking operation for a single reader with the parameters setted with touchatag_reader_led_blink_set.
 * If They aren't setted yet, default settings are used.
 */
void touchatag_reader_led_blink_target_reader (libusb_t *libusb, reader_t *reader, char *ID);

/** \brief Sets reader blinking parameters
 *
 * Colour can be:
 * 'r' -> red
 * 'g' -> green
 * 'o' -> orange
 * "Repetition" sets the number blinks.
 * "Time1" and "time2" sets the on/off frequency.
 */
void touchatag_reader_led_blink_set (char colour, int repetition, int time1, int time2);

/** \brief Sets the parameters for writing operationsù
 *
 * This function is used to set the parameters for writing operations.
 * "Size" describes the lenght of the string needed to write.
 * "Start" is the number of the byte from which writing operation has to begin.
 * "Note" is the array needed to write.
 * The given parameters have to respect the settings needed from the chosen writing function.
 */
void touchatag_reader_set_writing_notes (int size, int start, char *note, notes_t *notes);

/** \brief Prints reader ID
 *
 * This function prints reader ID.
 */
void touchatag_reader_print_reader_id (reader_t *reader);

/** \brief Returns the number of the handle linked to a reader
 *
 * This function returns the number of the handle linked to a reader.
 * This internal function is used from the library to link reader's uid to its handle (converts ID to TARGET).
 */
int touchatag_reader_link_id_reader_usb_handler (libusb_t *libusb, reader_t *reader, char *ID);

/** \brief Switches off the target reader
 *
 * This function switches off the voltage of the usb ports where the target reader is connected.
 */
void touchatag_reader_power_off_target_reader (libusb_t *libusb, reader_t *reader, char *ID);

/** \brief Prints reader's firmware
 *
 * This function prints the reader firmware of the given reader.
 */
void touchatag_reader_print_firmware (reader_t *reader);

/** \brief Prints reader's SAM identification number
 *
 * This function prints the reader SAM identification number of the given reader.
 */
void touchatag_reader_print_reader_identification_sam (reader_t *reader);

/** \brief Prints reader's SAM serial number
 *
 * This function prints the reader SAM serial number of the given reader.
 */
void touchatag_reader_print_reader_serial_sam (reader_t *reader);

/** \brief Returns reader's firmware (in ASCII)
 *
 * Returns reader firmware (in ASCII).
*/
char *touchatag_reader_return_reader_firmware (reader_t *reader);

/** \brief Returns reader ID (as string)
 *
 * Returns reader ID (as string).
*/
char *touchatag_reader_return_reader_id (reader_t *reader);

/** \brief Returns reader SAM identification number
 *
 * Returns reader SAM identification number.
*/
char *touchatag_reader_return_reader_identification_sam (reader_t *reader);

/** \brief Returns reader SAM serial number
 *
 * Returns reader SAM serial number.
*/
char *touchatag_reader_return_reader_serial_sam (reader_t *reader);

#endif /*LIBTOUCH_READER_H_*/
