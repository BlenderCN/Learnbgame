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

#include <sys/timeb.h>
#include <stdio.h>
#include "touchatag_time.h"
#define MAX_CONT 4


/*
 Returns the difference between the time of timeb given struct and the current time
*/
long int
touchatag_time_return_count_time (struct timeb *time_data)
{
	struct timeb temp;
	long int diff;
	
	/* Get current time */
	ftime (&temp);
	
	if (time_data->time == 0) {
		printf ("Begin missing\n");
		return -1;
	}

	/* Calculate diff time */
	diff = (temp.time * 1000 + temp.millitm) - (time_data->time * 1000 + time_data->millitm);
	
    return diff;
}


/*
 Starts counting process
 Data saved in the timeb given struct
*/
void
touchatag_time_begin_count (struct timeb *time_data)
{
	/* Get and save current time */
    ftime (time_data);
}
