# ------------------------------------------------------------------------------
# LICENSE
# ------------------------------------------------------------------------------
# Render+ - Blender addon
# (c) Copyright Diego Garcia Gangl (januz) - 2014, 2015
# <diego@sinestesia.co>
# ------------------------------------------------------------------------------
# This file is part of Render+
#
# Render+ is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
# ------------------------------------------------------------------------------

import time
import logging
import shutil
import os

from email.utils import formatdate

from . import control
from . import state

from .. import utils
from .. import data

# ------------------------------------------------------------------------------
#  VARIABLES
# ------------------------------------------------------------------------------

log = logging.getLogger(__name__)

feed_file = None
jobs = []

status = {
            'finished'  : False,
            'jobs_done' : 0,
         }

times = {
            'started'       : 0,
            'last_finished' : 0,
        }

feed_data = {
                'title'         : None,
                'last_updated'  : 0,
                'description'   : None,
                'completed'     : None,
                'progress'      : None,
                'items'         : []
            }


# ------------------------------------------------------------------------------
#  MANAGEMENT
# ------------------------------------------------------------------------------

def setup_feed(name, job_list):
    """ Setup feed information """
    
    global jobs
    
    now                      = utils.current_time() 
    feed_data['title']       = 'Batch Render: ' + name 
    feed_data['description'] = 'Batch started on: {0}.\n '.format(now)
    
    times['last_update']     = formatdate(localtime=True)
    times['started']         = time.time()
    
    jobs                     = job_list

    for job in jobs:
        job['status'] = state.Code.WAITING
        

def update(index, job_status):
    """ Update feed """
    
    jobs[index]['status']  = job_status
    times['last_finished'] = time.time()
    
    # Failed, Finished and Disabled count as
    # "done". All jobs start as Waiting so that
    # code would never be sent in an update
    if job_status != state.Code.RUNNING:
        status['jobs_done'] += 1
         
    if index + 1 == len(jobs):
        status['finished'] = True


def reset():
    """ Reset variables of this module """
    
    global feed_file
    feed_file = None
    
    jobs.clear()
    times.update({}.fromkeys(times, 0))
    feed_data.update({}.fromkeys(feed_data, None))
    
    status['finished'] = False
    status['jobs_done'] = 0
    

# ------------------------------------------------------------------------------
#  GENERATE
# ------------------------------------------------------------------------------

def calculate_progress():
    """ Calculate and format progress of the batch """

    estimated_remaining = ''
    estimated_text = ''
        
    if times['last_finished']:
        elapsed = times['last_finished'] - times['started']
        avg_time_per_job = elapsed / len(jobs)
            
        remaining_jobs = len(jobs) - status['jobs_done']
        estimated_remaining = avg_time_per_job * remaining_jobs
        estimated_remaining = utils.time_format(estimated_remaining)
        elapsed = utils.time_format(elapsed)
        estimated_text = 'estimated remaining.'
    else:
        elapsed = '0s'
        estimated_remaining = 'Unknown remaining.'
            
    if status['finished']:
        estimated_remaining = ''
        estimated_text = ''
            
        
    progress =  ('{0} of {1} jobs completed. '
                 '{2} elapsed. ' 
                 '{3} {4}')


    return progress.format( status['jobs_done'],
                            len(jobs),
                            elapsed,
                            estimated_remaining,
                            estimated_text,
                          )


def prepare_items_data():
    """ Prepare list of items for formatting """

    items = []
    guid = 1
    
    for job in jobs:
        item_data = {}

        # Title
        # ----------------------------------------------------------------------
        title = '[{0}] {1}'
        
        if not job['enabled']:
            prefix = 'DISABLED'
        elif job['status'] == state.Code.WAITING:
            prefix = 'QUEUED'
        elif job['status'] == state.Code.RUNNING:
            prefix = 'PROCESSING NOW'
        elif job['status'] == state.Code.FINISHED:
            prefix = 'FINISHED'
        elif job['status'] == state.Code.FAILED:
            prefix = 'FAILED'
            
        item_data['title'] = title.format(prefix, job['name'])
            
        # Description
        # ----------------------------------------------------------------------
        if job['status'] == state.Code.FAILED:
            description = 'FAILED on {0}\n\n'.format(utils.current_time())
        elif job['status'] == state.Code.FINISHED:
            description = 'FINISHED on {0}\n\n'.format(utils.current_time())
        else:
            description = ''
            
        item_data['description'] = description
        
        for key, value in job.items():
            if value == '' or value == 0 or key == 'custom_overrides':
                continue

            item_data['description'] += '{0} = {1}\n'.format(key, value) 

        if 'custom_overrides' in job and len(job['custom_overrides']) > 0:
            item_data['description'] += '\nCustom Overrides: \n'
                
            for over in job['custom_overrides']:
                item_data['description'] += '{0} = {1}\n'.format( over['path'],
                                                                  over['data'],
                                                                )
                                                                
        # GUID
        # ----------------------------------------------------------------------
        item_data['guid'] = guid
        guid += 1
        
        items.append(item_data)

    return items
    

def generate():
    """ Generate RSS code """
    
    # Prepare variables for formatting
    feed_data['progress']    = calculate_progress()    
    feed_data['last_update'] = formatdate(localtime=True)    
    feed_data['items']       = prepare_items_data()
    
    if status['finished']:
        feed_data['completed'] = 'Completed on: {0}.'.format(utils.current_time())
    
        
    # RSS Head
    template  = ('<?xml version="1.0" encoding="utf-8"?>\n'
                 '<?xml-stylesheet type="text/xsl" href="feed.xslt"?>\n'
                 '<rss version="2.0">\n'
                 '<channel>\n'

                 '<title>{title}</title>\n'
                 '<link>#</link>\n'
                 '<description>{description}{completed}</description>\n'
                 '<lastBuildDate>{last_update}</lastBuildDate>\n'
                 '<generator>Render+ 1.0</generator>\n')

    # Progress 
    template += ('<item>\n'
                 '<title>Progress</title>\n'
                 '<description>{progress}</description>\n'
                 '<guid>0</guid>\n'
                 '</item>\n'
                )
    
    
    # Jobs
    for index, job in enumerate(jobs):
        i = str(index)
        template += ('<item>\n'
                     '<title>{items['+i+'][title]}</title>\n'
                     '<description>{items['+i+'][description]}</description>\n'
                     '<guid>{items['+i+'][guid]}</guid>\n'
                     '</item>\n'
                    )
    
    # Close
    template += '</channel>\n</rss>'
            
    return template.format(**feed_data)

# ------------------------------------------------------------------------------
#  WRITE
# ------------------------------------------------------------------------------

def write():
    """ Write RSS file """
    
    try:
        with open(feed_file, 'w') as stream:
            stream.write(generate())
            
        # Copy Styles
        # ----------------------------------------------------------------------
        
        directory       = os.path.dirname(feed_file)
        dst_xslt        = os.path.join(directory, 'feed.xslt')
        dst_css         = os.path.join(directory, 'feed.css')
        src_xslt        = utils.path('assets', 'feed.xslt')
        use_custom_css  = data.prefs.batch_use_custom_css
            
        if use_custom_css and data.prefs.batch_custom_css != '':
            src_css  = data.prefs['batch_custom_css']
        else:
            src_css  = utils.path('assets', 'feed.css')
            
        shutil.copy2(src_xslt, dst_xslt)
        shutil.copy2(src_css, dst_css)
            
    except (PermissionError, FileNotFoundError, OSError) as e:
        msg = 'Can\'t write RSS feed file. Please check the filepath: '
        msg += feed_file
        msg += '\n Error: ' + str(e)
        log.error(msg)
