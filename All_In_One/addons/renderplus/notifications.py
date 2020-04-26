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

import os
import logging

import smtplib
from subprocess import Popen
from email.mime.text import MIMEText

import bpy
import aud
import bpy.props as prop

from . import utils
from . import data


# ------------------------------------------------------------------------------
# HANDLERS
# ------------------------------------------------------------------------------

# Sound notifications
sound_handle = None


# Logging
log = logging.getLogger(__name__)

# Errors
error = None


# ------------------------------------------------------------------------------
#  FUNCTIONS
# ------------------------------------------------------------------------------

def desktop(message = None):
    """ Send a desktop notification """

    if not message:
        filename = os.path.basename(bpy.data.filepath)
        message = filename + ' has finished rendering'
        
    command = ''

    if utils.sys == 'Linux':
        command = 'notify-send -i "blender" "Blender" ' + '"' + message + '"'
    elif utils.sys == 'Darwin':
        command = ('osascript -e \'display notification "' + message + '" \
                    with title "Blender"\'')

    log.debug('Desktop notification: ' + command)
    return Popen(command, shell=True)


def sound():
    """ Play a sound to notify """

    global sound_handle
    
    if data.prefs.sound_file == '':
        sound_file = utils.path('assets', 'notification.ogg')
    else:
        sound_file = utils.sane_path(data.prefs.sound_file)

    device = aud.device()
    factory = aud.Factory(sound_file)

    try:
        sound_handle = device.play(factory)
        sound_handle.volume = data.prefs.sound_volume / 100
    except aud.error as e:
        msg = 'Couldn\'t play sound file: ' + data.prefs.sound_file
        msg += '\n Error: ' + str(e)
        log.error(msg)


def log_error(msg):
    """ Log and show an error """

    global error

    if msg:
        error = msg
        log.error(msg)


def mail(message = None, subject = None):
    """ Send a notification via email """

    # Fail early if there's no email setup
    if 'mail_to' not in data.prefs:
        log.error(('Email hasn\'t been configured '
                  'yet! Check your preferences'))
        return

    # GENERATE MESSAGE
    server = None
    file = os.path.basename(bpy.data.filepath)
    stats = bpy.context.scene.renderplus.stats

    if file == '':
        file = 'Untitled'

    if not message:
        message = file + ' has finished rendering \n\n'
        
    message += 'Total render time: {0} seconds \n'.format(
        utils.time_format(
            stats.average))

    if stats.average > 0:
        message += 'Average frame time: ' + \
            str(utils.time_format(stats.average)) + ' seconds\n'
        message += 'Slowest frame: #{0} ({1} seconds)\n'.format(
            int(stats.slowest[0]), utils.time_format(stats.slowest[1]))

        message += 'Fastest frame: #{0} ({1} seconds)\n'.format(
            int(stats.fastest[0]), utils.time_format(stats.slowest[1]))

    # SETUP MAIL
    mail = MIMEText(message)

    if subject:
        mail['Subject'] = subject
    else:
        mail['Subject'] = file + ' has finished rendering'
        
    mail['From'] = 'Render+ Notifications <notify@render.plus>'
    mail['To'] = data.prefs['mail_to']

    # CONNECT AND SEND MAIL
    if data.prefs['mail_ssl']:
        server = smtplib.SMTP_SSL(data.prefs['mail_server'])
    else:
        server = smtplib.SMTP(data.prefs['mail_server'])

    try:
        server.login(data.prefs['mail_user'], data.prefs['mail_password'])
    except smtplib.SMTPAuthenticationError:
        msg = 'Username and/or password for email server are wrong. Please check your settings.'
        log.error(msg)
    except smtplib.SMTPException:
        msg = 'There was an error while trying to send the nofitication email.'
        log.error(msg)

    try:
        msg = ''
        server.send_message(mail)
    except smtplib.SMTPServerDisconnected:
        msg = 'Connection to email server was lost. Please try again.'
    except smtplib.SMTPRecipientsRefused:
        msg = 'The mail recipient was refused. Please check your settings and try again.'
    except (smtplib.SMTPDataError, smtplib.SMTPHeloError):
        msg = 'There was an error while trying to send the nofitication email.'
    except (smtplib.SMTPAuthenticationError, smtplib.SMTPSenderRefused):
        msg = 'Username and/or password for email server are wrong. Please check your settings.'
    finally:
        log_error(msg)
        server.quit()


class RP_OT_MailQuickSetup(bpy.types.Operator):
    bl_idname = 'renderplus.mail_quick_setup'
    bl_label = 'Mail quick setup'
    bl_description = 'Setup email automatically'
    bl_options = {'REGISTER'}

    provider = prop.EnumProperty(
        items=(('GMAIL', 'Gmail', ''),
               ('YAHOO', 'Yahoo', ''),
               ('LIVE', 'Live', '')
               ),
        default='GMAIL')

    def execute(self, context):

        if self.provider == 'GMAIL':
            data.prefs['mail_ssl'] = True
            data.prefs['mail_server'] = 'smtp.gmail.com'
            data.prefs['mail_user'] = '-YOU-@gmail.com'

        if self.provider == 'YAHOO':
            data.prefs['mail_ssl'] = True
            data.prefs['mail_server'] = 'smtp.mail.yahoo.com'
            data.prefs['mail_user'] = '-YOU-@yahoo.com'

        if self.provider == 'LIVE':
            data.prefs['mail_ssl'] = False
            data.prefs['mail_server'] = 'smtp.live.com'
            data.prefs['mail_user'] = '-YOU-@live.com'

        data.prefs['mail_password'] = '-YOUR-PASSWORD'

        return {'FINISHED'}
