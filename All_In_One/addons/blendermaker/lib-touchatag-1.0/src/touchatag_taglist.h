/** \file touchatag_taglist.h
*   \brief This header file contains every function related with tags SQLite database
*/
#ifndef TOUCHATAG_TAGLIST_H_
#define TOUCHATAG_TAGLIST_H_
#include "touchatag_tag.h"
#include <stdio.h>
#include <stdlib.h>
#include <sqlite3.h>

#define TAGLIST_ACTION_SIZE 101
#define TAGLIST_DATA_SIZE 101
#define TAGLIST_UID_SIZE 14


/*
 /struct Struct created to simplify reading operations from the database
 */
struct list_s {
	char uid[TAGLIST_UID_SIZE];       ///< Unique tag identification number (7 bytes -> 14 char)
	char data[TAGLIST_DATA_SIZE];     ///< Read/Write memory data (48 bytes - 96 char)
	char action[TAGLIST_ACTION_SIZE]; ///< Action used by the touchatag_taglist_execute_action ()
	int cont;                         ///< Integer used to count how many times the tag is used in any operation
	int num;                          ///< Unique autoincrementant key of the table
};

typedef struct list_s list_t;


/** \brief Creates the database
 * 
 * This function tries to create the database touchatag_db and a table named tag in the database named touchatag_db.
 * This table is composed by 5 columns: UID, DATA, ACTION, CONT, NUM (as struct list_t).
 * 
 * Returns 0 if the table has been created.
 * Returns -1 in event of troubles or if the table already exist.
 */ 
int touchatag_taglist_sqlite3_init ();

/** \brief Adds tag's data to a new row in the database table
 * 
 * This function uses attributes of the given tag's structure and the array pointed by act to add a row to the table
 * 
 * Returns 1 if the row has been added.
 * Returns 0 a row with the same uid already exist (in this case the function does nothing).
 * Returns -1 in event of errors.
 */ 
int touchatag_taglist_sqlite3_add (tag_t *tag, char *act);

/** \brief Allocates a new action linked to the tag given
 * This function uses attributes of the given tag structure and the array pointed to act 
 * to change the action linked to a tag with another contained in act
 * 
 * Returns 1 if the row has been added.
 * Returns -1 in event of errors
 */ 
int touchatag_taglist_sqlite3_action_update (tag_t *tag, char *act);

/** \brief Searches in the table a row with the given tag's uid (struct)
 *
 * This function looks for the given tag (struct) into the database.
 * 
 * Returns 1 if the tag UID is found.
 * Returns 0 if the tag UID is NOT found.
 * Returns -1 in event of errors
 */
int touchatag_touchatag_sqlite3_search (tag_t *tag);

/** \brief Searches in the table a row with the given tag's uid (as char*)
 *
 * This function looks for the given tag (as char *) into the database.
 * 
 * Returns 1 if the tag UID is found.
 * Returns 0 if the tag UID is NOT found.
 * Returns -1 in event of errors
 */
int touchatag_taglist_sqlite3_search_from_uid (char *tag_uid);

/** \brief Increments the value of the CONT section refered to the given tag (if the tag UID is in the DB)
 * 
 * This function increments the value of the CONT section refered to the given tag (if the tag UID is in the DB)
 * 
 * Returns 1 if the tag UID is found.
 * Returns 0 if the tag UID is NOT found.
 * Returns -1 in event of errors.
 */ 
int touchatag_taglist_sqlite3_update_counter_tag (tag_t *tag);

/** \brief Returns the value of CONT
 * 
 * This function returns the count value of the the given tag.
 * 
 * Returns -2 if the tag UID is NOT found.
 * Returns -1 in event of errors
 */ 
int touchatag_taglist_sqlite3_return_counter_tag (tag_t *tag);

/** \brief Deletes a row of the table
 * 
 * This function deletes the row with the UID of the given tag.
 * 
 * Returns 1 if the tag UID is found and the row is deleted.
 * Returns 0 if the tag UID is NOT found.
 * Returns -1 in case of errors.
 */
int touchatag_taglist_sqlite3_delete_tag (tag_t *tag);

/** \brief Deletes a row of the table
 * 
 * This function deletes the row with the UID of the given char data.
 * 
 * Returns 1 if the tag UID is found and the row is deleted.
 * Returns 0 if the tag UID is NOT found.
 * Returns -1 in case of errors.
 */
int touchatag_taglist_sqlite3_delete_tag_from_uid (char *tag_uid);

/** \brief Deletes the entire content of the table
 * 
 * This function deletes the entire content of the table but not the table itself.
 * 
 * Returns 1 if everything is done.
 * Returns -1 in event of errors.
 */
int touchatag_taglist_sqlite3_reset_db ();

/** \brief Prints the entire content of the table
 * 
 * This function prints the entire content of the table
 * 
 * Returns 1 if everything is done.
 * Returns -1 in event of errors.
 */
int touchatag_taglist_sqlite3_show_all ();

/** \brief Copies the action's value of a row into the given array
 * 
 * This function copies into the given array the action's value of the row with the given tag UID.
 * 
 * Returns 1 if the tag UID is found and the action copied.
 * Returns 0 if the tag UID is NOT found.
 * Returns -1 in event of errors.
 */
int touchatag_taglist_sqlite3_copy_action (tag_t *tag, char *res);

/** \brief Copies every rows of the table in a list_t type's array
 * 
 * This function copies every rows of the table in a list_t type's array
 * 
 * Returns 1 if everything is done.
 * Returns -1 in event of errors.
 */
int touchatag_taglist_sqlite3_save_all (list_t *lists);

/** \brief Returns how many rows are saved in the table
 * 
 * This function simply returns the number of row saved in the table.
 * 
 * Returns -1 in event of errors.
 */
int touchatag_taglist_sqlite3_number_rows ();

/** \brief Executes the tag "action"
 * 
 * This function executes the action written in the row with the given tag UID.
 * 
 * Returns 1 if everything is done.
 * Returns -1 in event of errors.
 */
int touchatag_taglist_execute_action0 (tag_t *tag, char *user);

/** \brief Saves tag's data in the given struct
 * 
 * This function saves in the given struct all the data belonging to the tag_uid given.
 */ 
int touchatag_taglist_sqlite3_save_info_tag (char *tag_uid, list_t *list);

/** \brief Internal function
 * 
 * This function generates from 1 hexadecimal character, 2 equivalent chars.
 */
void touchatag_sconvert (tag_t *tag, char *dest1, char *dest2);

#endif /*TOUCHATAG_TAGLIST_H_*/
