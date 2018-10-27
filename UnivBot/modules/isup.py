# coding=utf8
"""
isup.py - Simple website status check with isup.me
Author: Edward Powell http://embolalia.net
About: http://UnivBot.dftba.net

This allows users to check if a website is up through isup.me.
"""
from __future__ import unicode_literals

from UnivBot import web
from UnivBot.module import commands


@commands('isup')
def isup(bot, trigger):
    """isup.me website status checker"""
    site = trigger.group(2)
    if not site:
        return bot.reply("¿Que sitio web debo verificar?")

    if site[:6] != 'http://' and site[:7] != 'https://':
        if '://' in site:
            protocol = site.split('://')[0] + '://'
            return bot.reply("Intenta de nuevo sin el %s" % protocol)
        else:
            site = 'http://' + site
    try:
        response = web.get(site)
    except Exception:
        bot.say(site + ' parece caído desde aquí.')
        return

    if response:
        bot.say(site + ' está vivo desde aquí.')
    else:
        bot.say(site + ' parece caído desde aquí.')
