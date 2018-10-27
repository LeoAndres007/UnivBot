# coding=utf8
"""
admin.py - UnivBot Bugzilla Module
Copyright © 2013, Edward Powell, embolalia.net
Licensed under the Eiffel Forum License 2.

http://UnivBot.dftba.net/
"""
from __future__ import unicode_literals

from lxml import etree
import re
from UnivBot import web, tools
from UnivBot.module import rule


def configure(config):
    """

    | [bugzilla] | example | purpose |
    | ---- | ------- | ------- |
    | domains | bugzilla.redhat.com,bugzilla.mozilla.org | A list of Bugzilla issue tracker domains |
    """
    if config.option('Show extra information about Bugzilla issues', False):
        config.add_section('bugzilla')
        config.add_list('bugzilla', 'domains',
                        'Enter the domains of the Bugzillas you want extra '
                        'information from. (e.g. bugzilla.mozilla.org)',
                        'Domain:')


def setup(bot):
    regexes = []
    if not (bot.config.has_option('bugzilla', 'domains')
            and bot.config.bugzilla.get_list('domains')):
        return
    if not bot.memory.contains('url_callbacks'):
        bot.memory['url_callbacks'] = tools.UnivBotMemory()

    domains = '|'.join(bot.config.bugzilla.get_list('domains'))
    regex = re.compile((r'https?://(%s)'
                         '(/show_bug.cgi\?\S*?)'
                         '(id=\d+)')
                       % domains)
    bot.memory['url_callbacks'][regex] = show_bug


@rule(r'.*https?://(\S+?)'
       '(/show_bug.cgi\?\S*?)'
       '(id=\d+).*')
def show_bug(bot, trigger, match=None):
    """Muestra información de un bug."""
    match = match or trigger
    domain = match.group(1)
    if not bot.config.has_section('bugzilla') or domain not in bot.config.bugzilla.get_list('domains'):
        return
    url = 'https://%s%sctype=xml&%s' % match.groups()
    data = web.get(url, dont_decode=True)
    bug = etree.fromstring(data).find('bug')

    message = ('[BUGZILLA] %s | Producto: %s | Componente: %s | Versión: %s | ' +
               'Importancia: %s |  Estado: %s | Asignado a: %s | ' +
               'Reportado: %s | Modificado: %s')

    resolution = bug.find('resolution')
    if resolution is not None and resolution.text:
        status = bug.find('bug_status').text + ' ' + resolution.text
    else:
        status = bug.find('bug_status').text

    message = message % (
        bug.find('short_desc').text, bug.find('product').text,
        bug.find('component').text, bug.find('version').text,
        (bug.find('priority').text + ' ' + bug.find('bug_severity').text),
        status, bug.find('assigned_to').text, bug.find('creation_ts').text,
        bug.find('delta_ts').text)
    bot.say(message)