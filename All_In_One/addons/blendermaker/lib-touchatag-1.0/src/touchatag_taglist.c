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

#include <stdio.h>                 
#include <sqlite3.h>        
#include <string.h>
#include <unistd.h>
#include "touchatag_tag.h"					 
#include "touchatag_taglist.h"

#define MAX_LENGHT_ACTION 48
#define MAX_ARGS 5

char *zErr;
char dbname[] = "touchatag_db";
const unsigned char *res;

char uid[15];
char data[97];


/* 
 Creates db file (if i doesn't exist yet)
 To use at the beginning just one time
*/
int
touchatag_taglist_sqlite3_init ()
{	
	sqlite3 *database;
	int rc;
	
	if ((rc = sqlite3_open (dbname, &database)) != SQLITE_OK){
		printf ("Error sqlite3_open ()\n");
		return -1;
	}
	
	if ((rc = sqlite3_exec (database, "create table tag(UID text, DATA_MEMORY text, ACTION text, CONT int, NUM integer primary key autoincrement)", NULL, NULL, &zErr)) != SQLITE_OK){   
		sqlite3_close(database);                          
		return -1;
	}

	sqlite3_close (database);
	return 0;
}


/* 
 Looks in the db for the tag ID (given)
 Returns 1 if it finds the tag UID in the db
 Returns 0 if it doesn't find the tag in the db
 Returns -1 if there is an error
*/
int
touchatag_taglist_sqlite3_search (tag_t *tag)
{	
	sqlite3_stmt *pStmt;   
	sqlite3 *database;
	int rc, i = 0, b;

	if ((rc = sqlite3_open (dbname, &database)) != SQLITE_OK){
		printf ("Error sqlite3_open ()\n");
		return -1;
	}
	
	touchatag_sconvert (tag, uid, data);

	if ((rc = sqlite3_prepare_v2 (database, "SELECT * FROM tag WHERE UID=?", -1, &pStmt, NULL)) != SQLITE_OK){
		printf("Error prepare_v2 #1 search\n");
		return -1;
	}

	if ((rc = sqlite3_bind_text (pStmt, 1, uid, -1, NULL)) != SQLITE_OK){
		printf ("Error sqlite3_bind_text () in touchatag_taglist_sqlite3_search\n");
		return -1;
	}
	
	if ((rc = sqlite3_step (pStmt)) != SQLITE_ROW){

		i = sqlite3_clear_bindings (pStmt);

		if ((rc = sqlite3_reset (pStmt)) != SQLITE_OK){
			printf ("Error sqlite3_reset () in touchatag_taglist_sqlite3_search\n");
			return -1;
		}
		return 0;
	}

	i=sqlite3_clear_bindings (pStmt);
	
	if ((rc = sqlite3_reset (pStmt))!= SQLITE_OK){
		printf("Error sqlite3_reset () in touchatag_taglist_sqlite3_search\n");
		return -1;
	}
	return 1;
}


/* 
 Looks in the db for the tag ID (given)
 Returns 1 if it finds the tag UID in the db
 Returns 0 if it doesn't find the tag in the db
 Returns -1 if there is an error
*/
int
touchatag_taglist_sqlite3_search_from_uid (char *tag_uid)
{	
	sqlite3_stmt *pStmt;   
	sqlite3 *database;
	int rc, i = 0, b;

	if ((rc = sqlite3_open (dbname, &database)) != SQLITE_OK){
		printf ("Error sqlite3_open ()\n");
		return -1;
	}

	if ((rc = sqlite3_prepare_v2 (database, "SELECT * FROM tag WHERE UID=?", -1, &pStmt, NULL)) != SQLITE_OK){
		printf("Error prepare_v2 #1 search\n");
		return -1;
	}

	if ((rc = sqlite3_bind_text (pStmt, 1, tag_uid, -1, NULL)) != SQLITE_OK){
		printf ("Error sqlite3_bind_text () in touchatag_taglist_sqlite3_search\n");
		return -1;
	}
	
	if ((rc = sqlite3_step (pStmt)) != SQLITE_ROW){

		i = sqlite3_clear_bindings (pStmt);

		if ((rc = sqlite3_reset (pStmt)) != SQLITE_OK){
			printf ("Error sqlite3_reset () in touchatag_taglist_sqlite3_search\n");
			return -1;
		}
		return 0;
	}

	i=sqlite3_clear_bindings (pStmt);
	
	if ((rc = sqlite3_reset (pStmt))!= SQLITE_OK){
		printf ("Error sqlite3_reset () in touchatag_taglist_sqlite3_search\n");
		return -1;
	}
	return 1;
}


/* 
 Saves in ret the tag action if it exists
 Returns 0 if it doesn't exists
 Returns -1 if it there is an error
*/
int
touchatag_taglist_sqlite3_copy_action (tag_t *tag, char *ret)
{	
	sqlite3_stmt *pStmt;   
	sqlite3 *database;
	int rc, rf, i = 0;
	uid[14] = '\0';
	data[96] = '\0';

	if ((rc = sqlite3_open (dbname, &database)) != SQLITE_OK){
		printf ("Error sqlite3_open ()\n");
		return -1;
	}
	
	touchatag_sconvert (tag, uid, data);
		
	if ((rf = touchatag_taglist_sqlite3_search (tag)) == -1){
		printf ("Error touchatag_taglist_sqlite3_search ()\n");
		sqlite3_close (database);
		return -1;
	}
	
	if (rf == 0) {
		sqlite3_close (database);
		return 0;
	}
		
	if (rf == 1) {                                          
			
		if ((rc = sqlite3_prepare_v2 (database,"SELECT * from tag WHERE UID=?", -1, &pStmt, NULL)) != SQLITE_OK){   
			printf ("Error sqlite3_prepare_v2 ()\n");
			sqlite3_close (database); 
			return -1;
		}
		
		if ((rc = sqlite3_bind_text (pStmt, 1, uid, -1, NULL)) != SQLITE_OK){               
			printf ("Error sqlite3_bind_text ()\n");
			sqlite3_close (database); 
			return -1;
		}
		
		if ((rc = sqlite3_step (pStmt)) != SQLITE_ROW){                     
			printf ("Error sqlite3_step ()\n");
			return -1;
		}
		
		res = sqlite3_column_text (pStmt, 2);                 
		
		sprintf (ret, "%s", res);
			
		i = sqlite3_clear_bindings (pStmt);                            
		
		if ((rc = sqlite3_reset (pStmt)) != SQLITE_OK){    
			printf ("Error sqlite3_reset ()\n");
			sqlite3_close (database);
			return -1;
		}
			
		sqlite3_close (database); 
		return 1;
	}
}


/*
 Looks for the given iag UID in the database.
 If doesn't exist yet, the func inserts it in the db with the linked action.
 If it exists, the func just replace the action
*/
int
touchatag_taglist_sqlite3_action_update (tag_t *tag, char *act)
{
	sqlite3_stmt *pStmt;   
	sqlite3 *database;
	int rc, rf, i = 0;
	char *pa = act;
	
	uid[14]='\0';
	data[96]='\0';

	if ((rc = sqlite3_open (dbname, &database)) != SQLITE_OK){
		printf ("Error sqlite3_open ()\n");
		return -1;
	}
	
	touchatag_sconvert (tag, uid, data);
	
	if ((rf = touchatag_taglist_sqlite3_search (tag)) == -1){
		printf("Error touchatag_taglist_sqlite3_search () in touchatag_taglist_sqlite3_action_update ()\n");
		sqlite3_close(database);
		return -1;
	}
	
	if (rf==0) {
		if ((rc = sqlite3_prepare_v2 (database, "INSERT INTO tag VALUES (?,?,?,0,NULL)", -1, &pStmt, NULL)) != SQLITE_OK){    
			printf("Error sqlite3_prepare_v2 () #1 in touchatag_taglist_sqlite3_action_update ()\n");
			sqlite3_close (database);
			return -1;
		}
		if ((rc = sqlite3_bind_text (pStmt, 1, (const char*)uid, -1, NULL)) != SQLITE_OK){        
			printf("Error sqlite3_bind_text () #1 in touchatag_taglist_sqlite3_action_update ()\n");
			sqlite3_close(database);
			return -1;
		}
		if ((rc = sqlite3_bind_text (pStmt, 2, (const char*)data, -1, NULL)) != SQLITE_OK){
			printf("Error sqlite3_bind_text () #2 in touchatag_taglist_sqlite3_action_update ()\n");
			sqlite3_close(database);
			return -1;
		}
		if ((rc = sqlite3_bind_text (pStmt, 3, (const char*)pa, -1, NULL)) != SQLITE_OK){ 
			printf("Error sqlite3_bind_text () #3 in touchatag_taglist_sqlite3_action_update\n");
			sqlite3_close(database);
			return -1;
		}		
	}
	if (rf == 1) {
		if ((rc = sqlite3_prepare_v2 (database,"UPDATE tag SET ACTION=? WHERE UID=?", -1, &pStmt, NULL)) != SQLITE_OK){       
			printf("Error sqlite3_prepare_v2 () #2 in touchatag_taglist_sqlite3_action_update ()\n");
			sqlite3_close(database);
			return -1;
		}
		if ((rc = sqlite3_bind_text (pStmt, 1, (const char*)pa, -1, NULL)) != SQLITE_OK){
			printf("Error sqlite3_bind_text () #4 in touchatag_taglist_sqlite3_action_update ()\n");
			sqlite3_close(database);
			return -1;
		}
		if ((rc = sqlite3_bind_text (pStmt, 2, (const char*)uid, -1, NULL)) != SQLITE_OK){
			printf("Error sqlite3_bind_text () #5 in touchatag_taglist_sqlite3_action_update ()\n");
			sqlite3_close(database);
			return -1;
		}
	}
	
	if ((rc = sqlite3_step (pStmt)) != SQLITE_DONE){
		printf("Error sqlite3_step () in touchatag_taglist_sqlite3_action_update ()\n");
		sqlite3_close(database);
		return -1;
	}
	
	i=sqlite3_clear_bindings (pStmt);                             
		
	if ((rc = sqlite3_reset (pStmt))!= SQLITE_OK){
		printf("Error sqlite3_reset ()\n");
		sqlite3_close(database);
		return -1;
	}
	
	sqlite3_close(database); 
	return 1;
}


/*
 * TOUCHATAG_SQLITE3_ADD                            
 dato un tag e un azione, se il tag non è nel db lo mette nel db con l'azione voluta e ritorna 1. altrimenti non fa niente e ritorna 0; se errore -1
*/
int
touchatag_sqlite3_add (tag_t *tag, char *act)
{
	sqlite3_stmt *pStmt;   
	sqlite3 *database;
	int rc, rf, i = 0;
	char *pa = act;	
	
	uid[14]='\0';
	data[96]='\0';

	if ((rc = sqlite3_open (dbname, &database)) != SQLITE_OK){
		printf ("Error sqlite3_open ()\n");
		return -1;
	}
	
	touchatag_sconvert (tag, uid, data);

	if ((rf = touchatag_taglist_sqlite3_search (tag)) == -1){
		printf ("Error touchatag_taglist_sqlite3_search ()\n");
		sqlite3_close (database);
		return -1;
	}
	if (rf == 0) {
		if ((rc = sqlite3_prepare_v2 (database, "INSERT INTO tag VALUES (?,?,?,0,NULL)", -1, &pStmt, NULL)) != SQLITE_OK){
			printf ("Error sqlite3_prepare_v2 ()\n");
			sqlite3_close (database);
			return -1;
		}
		if ((rc = sqlite3_bind_text (pStmt, 1, (const char*) uid, -1, NULL)) != SQLITE_OK){
			printf ("Error sqlite3_bind_text () #1\n");
			sqlite3_close (database);
			return -1;
		}
		if ((rc = sqlite3_bind_text (pStmt, 2, (const char*) data, -1, NULL)) != SQLITE_OK){
			printf ("Error sqlite3_bind_text () #2\n");
			sqlite3_close (database);
			return -1;
		}
		if ((rc = sqlite3_bind_text (pStmt, 3, (const char*) pa, -1, NULL)) != SQLITE_OK){         
			printf ("Error sqlite3_bind_text () #3\n");
			sqlite3_close (database);
			return -1;
		}		
	}
	if (rf == 1) {
		sqlite3_close (database); 
		return 0;
	}
	if ((rc = sqlite3_step (pStmt)) != SQLITE_DONE){
		printf ("Error sqlite3_step ()\n");
		sqlite3_close (database);
		return -1;
	}
	
	i = sqlite3_clear_bindings (pStmt); 
		
	if ((rc = sqlite3_reset (pStmt))!= SQLITE_OK){
		printf ("Errore sqlite3_reset ()\n");
		sqlite3_close (database);
		return -1;
	}
	sqlite3_close (database); 
	return 1;
}


/*
 Update (plus 1) the counter of the given tag (if it exists in the db)
 Returns 0 if it's not in the db
 Returns -1 if there is a problem
*/
int
touchatag_taglist_sqlite3_update_counter_tag (tag_t *tag)
{
	sqlite3_stmt *pStmt;   
	sqlite3 *database;
	int rc, rf, i = 0;
	
	uid[14] = '\0';
	data[96] = '\0';

	if ((rc = sqlite3_open (dbname, &database)) != SQLITE_OK){
		printf ("Error sqlite3_open ()\n");
		return -1;
	}
	
	touchatag_sconvert (tag, uid, data);

	if ((rf = touchatag_taglist_sqlite3_return_counter_tag (tag)) == -1){
		printf ("Error touchatag_taglist_sqlite3_return_counter_tag () in touchatag_taglist_sqlite3_update_counter_tag ()\n");
		sqlite3_close (database);
		return -1;
	}
	if (rf == -2) {
		sqlite3_close (database);
		return 0;
	}		
			
	rf++;          
		
	if ((rc = sqlite3_prepare_v2 (database,"UPDATE tag SET CONT=? WHERE UID=?", -1, &pStmt, NULL)) != SQLITE_OK){
		printf ("Error sqlite3_prepare_v2 () in touchatag_taglist_sqlite3_update_counter_tag ()\n");
		sqlite3_close (database);
		return -1;
	}
	if ((rc = sqlite3_bind_int (pStmt, 1, rf)) != SQLITE_OK){
		printf ("Error sqlite3_bind_int () in touchatag_taglist_sqlite3_update_counter_tag ()\n");
		sqlite3_close (database);
		return -1;
	}
	if ((rc = sqlite3_bind_text (pStmt, 2, (const char*)uid, -1, NULL)) != SQLITE_OK){
		printf ("Error sqlite3_bind_text () in touchatag_taglist_sqlite3_update_counter_tag ()\n");
		sqlite3_close (database);
		return -1;

	}
	if ((rc = sqlite3_step (pStmt)) != SQLITE_DONE){
		printf ("Error sqlite3_step () in touchatag_taglist_sqlite3_update_counter_tag ()\n");
		sqlite3_close (database);
		return -1;
	}
	
	i = sqlite3_clear_bindings (pStmt);
		
	if ((rc = sqlite3_reset (pStmt))!= SQLITE_OK){
		printf ("Error sqlite3_reset () in touchatag_taglist_sqlite3_update_counter_tag ()\n");
		sqlite3_close (database);
		return -1;
	}
	
	sqlite3_close (database); 
	return 1;
}


/* 
 Returns tag counter value
 Returns -2 it the tag is not in the db
*/
int
touchatag_taglist_sqlite3_return_counter_tag (tag_t *tag)
{	
	sqlite3_stmt *pStmt;   
	sqlite3 *database;
	int rc, rf, i = 0, id;
	
	uid[14] = '\0';
	data[96] = '\0';

	if ((rc = sqlite3_open (dbname, &database)) != SQLITE_OK){
		printf ("Error sqlite3_open ()\n");
		return -1;
	}
	
	touchatag_sconvert (tag, uid, data);
	
	if ((rf = touchatag_taglist_sqlite3_search (tag)) == -1){    
		printf ("Errore touchatag_taglist_sqlite3_search () in touchatag_taglist_sqlite3_return_counter_tag ()\n");
		sqlite3_close (database);
		return -1;
	}
	
	if (rf == 0) {
		sqlite3_close (database); 
		return -2;
	}
		
	if (rf == 1) {
	
		if ((rc = sqlite3_prepare_v2 (database, "SELECT * from tag WHERE UID=?", -1, &pStmt, NULL)) != SQLITE_OK){
			printf ("Error sqlite3_prepare_v2 () in touchatag_taglist_sqlite3_return_counter_tag ()\n");
			sqlite3_close (database); 
			return -1;
		}
		
		if ((rc = sqlite3_bind_text (pStmt, 1, uid, -1, NULL)) != SQLITE_OK){
			printf ("Error sqlite3_bind_text () in touchatag_taglist_sqlite3_return_counter_tag ()\n");
			sqlite3_close (database); 
			return -1;
		}
		
		if ((rc = sqlite3_step (pStmt)) != SQLITE_ROW){
			printf ("Error sqlite3_step () in touchatag_taglist_sqlite3_return_counter_tag ()\n");
			return -1;
		}
		
		id = sqlite3_column_int (pStmt, 3);
		
		i=sqlite3_clear_bindings (pStmt);   
				
		if ((rc = sqlite3_reset (pStmt)) != SQLITE_OK){
			printf ("Error sqlite3_reset () in touchatag_taglist_sqlite3_return_counter_tag ()\n");
			sqlite3_close (database);
			return -1;
		}
		sqlite3_close (database); 
		return id;
	}
}


/*
 Deletes the given tag from the db
 Returns 1 if it existed
 Returns 0 if the tag in not in the db
*/
int
touchatag_taglist_sqlite3_delete_tag (tag_t *tag)
{
	sqlite3_stmt *pStmt;   
	sqlite3 *database;
	int rc, rf, i = 0;
	const unsigned char *id;
	
	uid[14] = '\0';
	data[96] = '\0';

	if ((rc = sqlite3_open (dbname, &database)) != SQLITE_OK){
		printf ("Error sqlite3_open ()\n");
		return -1;
	}

	touchatag_sconvert (tag, uid, data);
	
	if ((rf = touchatag_taglist_sqlite3_search (tag)) == -1){      
		printf ("Errore touchatag_taglist_sqlite3_search () in touchatag_taglist_sqlite3_delete_tag ()\n");
		sqlite3_close (database);
		return -1;
	}
	
	if (rf == 0) {
		sqlite3_close (database); 
		return 0;
	}
		
	if (rf == 1) {
		if ((rc = sqlite3_prepare_v2 (database, "DELETE from tag WHERE UID=?", -1, &pStmt, NULL)) != SQLITE_OK){
			printf ("Error sqlite3_prepare_v2 () in touchatag_taglist_sqlite3_delete_tag ()\n");
			sqlite3_close (database); 
			return -1;
		}
		
		if ((rc = sqlite3_bind_text (pStmt, 1, uid, -1, NULL)) != SQLITE_OK){
			printf ("Error sqlite3_bind_text () in touchatag_taglist_sqlite3_delete_tag ()\n");
			sqlite3_close (database); 
			return -1;
		}
		
		if ((rc = sqlite3_step (pStmt)) != SQLITE_DONE){
			printf ("Error sqlite3_step () in touchatag_taglist_sqlite3_delete_tag ()\n");
			return -1;
		}
		
		i = sqlite3_clear_bindings (pStmt);
				
		if ((rc = sqlite3_reset (pStmt))!= SQLITE_OK){
			printf ("Error sqlite3_reset () in touchatag_taglist_sqlite3_delete_tag ()\n");
			sqlite3_close (database);
			return -1;
		}
			
		sqlite3_close (database); 
		return 1;
	}
}


/*
 Deletes the given tag from the db
 Returns 1 if it existed
 Returns 0 if the tag in not in the db
*/
int
touchatag_taglist_sqlite3_delete_tag_from_uid (char *tag_uid)
{
	sqlite3_stmt *pStmt;   
	sqlite3 *database;
	int rc, rf, i = 0;
	const unsigned char *id;
	
	if ((rc = sqlite3_open (dbname, &database)) != SQLITE_OK){
		printf ("Error sqlite3_open () in touchatag_taglist_sqlite3_delete_tag ()\n");
		sqlite3_close (database); 
		return -1;
	}
	
	if ((rf = touchatag_taglist_sqlite3_search_from_uid (tag_uid)) == -1){      
		printf ("Errore touchatag_taglist_sqlite3_search () in touchatag_taglist_sqlite3_delete_tag ()\n");
		sqlite3_close (database);
		return -1;
	}
	
	if (rf == 0) {
		sqlite3_close (database); 
		return 0;
	}
		
	if (rf == 1) {
		if ((rc = sqlite3_prepare_v2 (database, "DELETE from tag WHERE UID=?", -1, &pStmt, NULL)) != SQLITE_OK){
			printf ("Error sqlite3_prepare_v2 () in touchatag_taglist_sqlite3_delete_tag ()\n");
			sqlite3_close (database); 
			return -1;
		}
		
		if ((rc = sqlite3_bind_text (pStmt, 1, tag_uid, -1, NULL)) != SQLITE_OK){
			printf ("Error sqlite3_bind_text () in touchatag_taglist_sqlite3_delete_tag ()\n");
			sqlite3_close (database); 
			return -1;
		}
		
		if ((rc = sqlite3_step (pStmt)) != SQLITE_DONE){
			printf ("Error sqlite3_step () in touchatag_taglist_sqlite3_delete_tag ()\n");
			return -1;
		}
		
		i = sqlite3_clear_bindings (pStmt);
				
		if ((rc = sqlite3_reset (pStmt))!= SQLITE_OK){
			printf ("Error sqlite3_reset () in touchatag_taglist_sqlite3_delete_tag ()\n");
			sqlite3_close (database);
			return -1;
		}
			
		sqlite3_close (database); 
		return 1;
	}
}


/* 
 Deletes everything in the database
 Returns 1 if everything is done
 Returns -1 if there is an error
*/
int
touchatag_taglist_sqlite3_reset_db ()
{
	sqlite3_stmt *pStmt;   
	sqlite3 *database;
	int rc, rf, i = 0;
	const unsigned char *id;

	uid[14]='\0';
	data[96]='\0';
		
	if ((rc = sqlite3_open (dbname, &database)) != SQLITE_OK){
		printf ("Error sqlite3_open () in touchatag_taglist_sqlite3_reset_db ()\n");
		sqlite3_close (database); 
		return -1;
	}
		
	if ((rc = sqlite3_prepare_v2 (database,"DELETE from tag", -1, &pStmt, NULL)) != SQLITE_OK){
		printf ("Error sqlite3_prepare_v2 () in touchatag_taglist_sqlite3_reset_db ()\n");
		sqlite3_close (database); 
		return -1;
	}
	
	if ((rc = sqlite3_step (pStmt)) != SQLITE_DONE){
		printf ("Error sqlite3_step () in touchatag_taglist_sqlite3_reset_db ()\n");
		return -1;
	}
		
	if ((rc = sqlite3_reset (pStmt))!= SQLITE_OK){
		printf ("Error sqlite3_reset () in touchatag_taglist_sqlite3_reset_db ()\n");
		sqlite3_close (database);
		return -1;
	}
		
	sqlite3_close(database); 
	return 1;
}


/* 
 Prints all db data
 Returns 1 if everything is ok
 Riturns -1 if there is an error
*/
int
touchatag_taglist_sqlite3_show_all ()
{
	sqlite3 *database;
	char **result;
	char *zErrMsg = 0;
	int nrow;
 	int ncol;
	int i, rc, j;
 		
	if ((rc = sqlite3_open (dbname, &database)) != SQLITE_OK){
		printf("Error sqlite3_open () in touchatag_taglist_sqlite3_show_all ()\n");
		sqlite3_close (database); 
		return -1;
	}
	rc = sqlite3_get_table (database,"SELECT * from tag", &result, &nrow, &ncol, &zErrMsg);
	for (j = 0; j < nrow + 1; j++) {
		printf ("\n");
		for (i = 0 ; i < ncol; i++)
			printf("%s ",result[ncol*j + i]);
	}
  	printf ("\n");
  	sqlite3_free_table (result);
	
	sqlite3_close(database); 
	return 1;
}


/*
 Copies db rows in a list_t type's array
*/
int
touchatag_taglist_sqlite3_save_all (list_t *lists)
{
	sqlite3 *database;
	char **result;
	char *zErrMsg = 0;
	char buff[250];
	int nrow;
 	int ncol;
	int i, rc, j, k = 0;
	
	if ((rc = sqlite3_open (dbname, &database)) != SQLITE_OK){
		printf ("Error sqlite3_open () in touchatag_taglist_sqlite3_save_all ()\n");
		sqlite3_close (database);
		return -1;
	}
	
	rc = sqlite3_get_table (database, "SELECT * from tag", &result, &nrow, &ncol, &zErrMsg);
	
	for (j = 1; j < nrow + 1; j++) {
			sprintf (lists[k].uid, "%s", result[ncol*j]);
//			if (result[ncol*j+1] != NULL)
//				sprintf (lists[k].data,"%s",result[ncol*j+1]);
		
			sprintf (lists[k].action, "%s", result[ncol*j+2]);
			lists[k].cont = *result[ncol*j+3] - 48;
			lists[k].num = *result[ncol*j+4] - 48;
			k++;
	}
	
  	sqlite3_free_table (result);

	sqlite3_close (database);

	return 1;
}


/* 
 Returns tag counter value
 Returns -2 it the tag is not in the db
*/
int
touchatag_taglist_sqlite3_save_info_tag (char *tag_uid, list_t *list)
{	
	sqlite3_stmt *pStmt;   
	sqlite3 *database;
	int rc, rf, i = 0, count;
	
	if ((rc = sqlite3_open (dbname, &database)) != SQLITE_OK){
		printf ("Error sqlite3_open ()\n");
		sqlite3_close (database); 
		return -1;
	}
	
	if ((rf = touchatag_taglist_sqlite3_search_from_uid (tag_uid)) == -1){    
		printf ("Errore touchatag_taglist_sqlite3_search () in touchatag_taglist_sqlite3_return_counter_tag ()\n");
		sqlite3_close (database);
		return -1;
	}
	
	if (rf == 0) {
		sqlite3_close (database); 
		return -2;
	}
		
	if (rf == 1) {
	
		if ((rc = sqlite3_prepare_v2 (database, "SELECT * from tag WHERE UID=?", -1, &pStmt, NULL)) != SQLITE_OK){
			printf ("Error sqlite3_prepare_v2 () in touchatag_taglist_sqlite3_return_counter_tag ()\n");
			sqlite3_close (database); 
			return -1;
		}
		
		if ((rc = sqlite3_bind_text (pStmt, 1, tag_uid, -1, NULL)) != SQLITE_OK){
			printf ("Error sqlite3_bind_text () in touchatag_taglist_sqlite3_return_counter_tag ()\n");
			sqlite3_close (database); 
			return -1;
		}
		
		if ((rc = sqlite3_step (pStmt)) != SQLITE_ROW){
			printf ("Error sqlite3_step () in touchatag_taglist_sqlite3_return_counter_tag ()\n");
			return -1;
		}

		/* Saving data */
		sprintf (list->uid, "%s", sqlite3_column_text (pStmt, 0));
		sprintf (list->action, "%s", sqlite3_column_text (pStmt, 2));
		list->cont = sqlite3_column_int (pStmt, 3);
		list->num = sqlite3_column_int (pStmt, 4);

		i = sqlite3_clear_bindings (pStmt);   
				
		if ((rc = sqlite3_reset (pStmt)) != SQLITE_OK){
			printf ("Error sqlite3_reset () in touchatag_taglist_sqlite3_return_counter_tag ()\n");
			sqlite3_close (database);
			return -1;
		}
		sqlite3_close (database); 
	}
	return 1;
}


/* 
 Returns the number of rows
 Returns -1 if there is an error
*/
int
touchatag_taglist_sqlite3_number_rows ()
{
	sqlite3 *database;
	char **result;
	char *zErrMsg = 0;
	int nrow;
 	int ncol;
	int i, rc;
	
	if ((rc = sqlite3_open (dbname, &database)) != SQLITE_OK){
		printf ("Error sqlite3_open ()\n");
		sqlite3_close (database); 
		return -1;
	}
	
	rc = sqlite3_get_table (database,"SELECT * from tag", &result, &nrow, &ncol, &zErrMsg);
	
  	sqlite3_free_table (result);
	
	sqlite3_close (database);
	
	return nrow;
}


/* 
 * TOUCHATAG_execute   versione in prova (con una parte tratta da un esempio trovato in rete)      
*/
int touchatag_taglist_execute_action0 (tag_t *tag, char *user)
{
	int q, i=0;
	char action[100];
	char d[] = " ";
	char *args[MAX_ARGS];
	char *env[1];
	pid_t pid;

	/* Get action */
	q = touchatag_taglist_sqlite3_copy_action (tag, action);

	/* Look for errors */
	if (q == -1) {
		printf ("Error touchatag_taglist_sqlite3_copy_action () in touchatag_taglist_execute_action ()\n");
		return -1;
	}
	else if (q == 0) {
		printf ("Tag not in the DB\n");
		return 0;
	}
       	
	args[0] = strtok (action, d);
	printf ("args[0]: %s\n", args[0]);
	
	while((args[i] != NULL) || (i < MAX_ARGS)) {
		i++;
		args[i] = strtok (NULL, d);
		printf ("args[%d]: %s\n", i, args[i]);
	}

	env[0] = user;
	env[1] = NULL;
	printf ("env[1]: %s\n", env[1]);
	printf ("user: %s\n", user);

	pid = fork ();
	
	if (pid == 0) {
        /* Son */
        int ret;

        ret = execvp (args[0], args);
	    if (ret == -1)
	        perror ("execvp");
		
    }
    else if (pid == -1)
		printf (" Error fork ()\n");

	return 0;
}


/* 
 Generates from 1 hexadecimal character, 2 equivalent charTOUCHATAG_sconvert       
*/
void
touchatag_sconvert (tag_t *tag, char *dest1, char *dest2)
{
	char a[10];
	int i, z;
	for(i = 0; i < 7; i++) {
		z = sprintf (a, "%02x", tag->uid[i]);
		
		dest1[2*i] = a[z-2];
		dest1[2*i+1] = a[z-1];
		
		z = sprintf (a, "%02x", tag->data[i+16]);
	
		dest2[2*i] = a[z-2];
 		dest2[2*i+1] = a[z-1];
	}
	while (i < 48) {
		z = sprintf (a, "%02x", tag->data[i+16]);	

		dest2[2*i] = a[z-2];
 		dest2[2*i+1] = a[z-1];
		i++;
	}
}