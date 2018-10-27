# -*- coding: utf-8 -*-
"""
rae.py - UnivBot Real Academia española dictionary Module
Author: Miguel Peláez Tamayo
"""
from __future__ import unicode_literals
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import UnivBot.module
from opensearch import Client

@UnivBot.module.commands('define', 'rae', 'whatis')
def define(bot, trigger):
    """
    Da la definición de un término segun rae.
    """
    if not trigger.group(2):
        bot.say(trigger.nick + ': debes indicar un término a buscar en el diccionario.')
        return
    try:
	word = trigger.group(2)
        client = Client('http://dirae.es/static/opensearch.xml')
        results = client.search(word)

        max = 0
        for result in results:
            max = max + 1
            if result.title == word:
                output = result.summary
                url = 'http://lema.rae.es/drae/srv/search?val='+word
            elif max > 3:
                break
        if output:
            bot.say(output.replace('<em>', '\002').replace('</em>', '\002'))
            bot.say(url)
        else:
           bot.say('No he encontrado ese término!')
    except Exception as e:
        bot.say(trigger.nick + ': No pude obtener la definición de ese término, lo siento.')
        print "{error}: {msg}".format(error=type(e), msg=e)
