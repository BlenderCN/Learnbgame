/**\file touchatag_time.h
*\brief This header file contains every function related with timing
*/
#ifndef TOUCHATAG_TIME_H_
#define TOUCHATAG_TIME_H_
#include <sys/timeb.h>

/** \brief Starts a time count
 * 
 * This function starts a time count. It sets in timeb *time_data the current time.
 */
void touchatag_time_begin_count (struct timeb *time_data);

/** \brief Returns the difference between the time given and the current time
 * 
 * Returns (in milliseconds) the difference between the time of timeb *time_data and the current time.
 */
long int touchatag_time_return_count_time (struct timeb *time_data);

#endif /*TOUCHATAG_TIME_H_*/
