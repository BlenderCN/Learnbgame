# -*- coding: utf-8 -*-   
import bpy

bl_info = {
    "name": "Shutdown after Render",
    "description": "windows",
    "author": "CoDEmanX",
    "version": (1, 0),
    "blender": (2, 75, 0),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame"
}

import bpy
import os
from bpy.app.handlers import persistent
import smtplib

'''
Если у Вас не уходит почта через gmail/rambler/mail/yandex из-за отсутствия сертификатов этих почтовых сервисов.
 (Нажмите, чтобы показать/скрыть)
Возьмём, к примеру, почту gmail. Как достать их сертификат?
$openssl s_client -starttls smtp -crlf -connect smtp.gmail.com:25
выведется много всего интересного, но главное добавить содержимое между
-----BEGIN CERTIFICATE----- и -----END CERTIFICATE-----(включительно)
к себе в /etc/postfix/cacert.pem
и после этого почта уходила в мир без проблем
'''

@persistent
def render_complete_handler_nt(dummy):
    sender = 'email@yandex.ru'
    receivers = ['email@yandex.ru']

    message = """From: Work <email@yandex.ru>
    To: Nikitka <email@yandex.ru>
    Subject: Work is done, comp is off

    Твой рендер сохранён на компьютере, ты можешь быть спокоен, компьютер выключен,носки поглажены.
    """

    try:
        smtpObj = smtplib.SMTP_SSL( 'smtp.yandex.ru' , 465, timeout=120 )
        smtpObj.login("login", "passwd")
        smtpObj.sendmail(sender, receivers, message)         
        smtpObj.quit()
        print ("Successfully sent email")
    except:
        print ("Error: unable to send email")
    os.system("shutdown /s") # shutdown command here for linux 'poweroff'

def register():
    bpy.app.handlers.render_complete.append(render_complete_handler_nt)


def unregister():
    bpy.app.handlers.render_complete.remove(render_complete_handler_nt)

if __name__ == "__main__":
    register()
