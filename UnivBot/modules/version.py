# coding=utf8
"""
version.py - UnivBot Version Module
Copyright 2009, Silas Baronda
Copyright 2014, Dimitri Molenaars <tyrope@tyrope.nl>
Licensed under the Eiffel Forum License 2.

http://UnivBot.dftba.net
"""
from __future__ import unicode_literals

from datetime import datetime
import UnivBot
import re
from os import path
import json

log_line = re.compile('\S+ (\S+) (.*? <.*?>) (\d+) (\S+)\tcommit[^:]*: (.+)')


def git_info():
    repo = path.join(path.dirname(path.dirname(path.dirname(__file__))), '.git')
    head = path.join(repo, 'HEAD')
    if path.isfile(head):
        with open(head) as h:
            head_loc = h.readline()[5:-1]  # strip ref: and \n
        head_file = path.join(repo, head_loc)
        if path.isfile(head_file):
            with open(head_file) as h:
                sha = h.readline()
                if sha:
                    return sha


@UnivBot.module.commands('version')
def version(bot, trigger):
    """Display the latest commit version, if UnivBot is running in a git repo."""
    release = UnivBot.__version__
    sha = git_info()
    if not sha:
        msg = 'DreamBot ' + release
        if release[-4:] == '-git':
            msg += ' en un commit desconocido.'
        bot.reply(msg)
        return

    bot.reply("DreamBot v. {} en commit: {}".format(UnivBot.__version__, sha))


@UnivBot.module.rule('\x01VERSION\x01')
@UnivBot.module.rate(20)
def ctcp_version(bot, trigger):
    bot.write(('NOTICE', trigger.nick),
              '\x01VERSION DreamBot IRC Bot version %s\x01' % UnivBot.__version__)


@UnivBot.module.rule('\x01SOURCE\x01')
@UnivBot.module.rate(20)
def ctcp_source(bot, trigger):
    bot.write(('NOTICE', trigger.nick),
              '\x01SOURCE https://github.com/inteliBOT/pyDreamBot/\x01')


@UnivBot.module.rule('\x01PING\s(.*)\x01')
@UnivBot.module.rate(10)
def ctcp_ping(bot, trigger):
    text = trigger.group()
    text = text.replace("PING ", "")
    text = text.replace("\x01", "")
    bot.write(('NOTICE', trigger.nick),
              '\x01PING {0}\x01'.format(text))


@UnivBot.module.rule('\x01TIME\x01')
@UnivBot.module.rate(20)
def ctcp_time(bot, trigger):
    dt = datetime.now()
    current_time = dt.strftime("%A, %d. %B %Y %I:%M%p")
    bot.write(('NOTICE', trigger.nick),
              '\x01TIME {0}\x01'.format(current_time))
