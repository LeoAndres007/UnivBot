# coding=utf8
"""
find_updates.py - Update checking module for UnivBot.

This is separated from version.py, so that it can be easily overridden by
distribution packagers, and they can check their repositories rather than the
UnivBot website.
"""
# Copyright 2014, Edward D. Powell, embolalia.net
# Licensed under the Eiffel Forum License 2.
from __future__ import unicode_literals

import json
import re

import UnivBot
import UnivBot.module
import UnivBot.web

wait_time = 24 * 60 * 60  # check once per day
startup_check_run = False
version_url = 'http://UnivBot.dftba.net/latest.json'
message = (
    'La nueva versión de DreamBot {}, está disponible. Estoy ejecutando la {}. Por favor actualizame :) ' +
    'me. Full release notes at {}.'
)


def parse_version(version):
    return re.match('(\d+)\.(\d+)\.(\d+)(?:-\S+)?', version).groups()


@UnivBot.module.event('001')
@UnivBot.module.event('251')
@UnivBot.module.rule('.*')
def startup_version_check(bot, trigger):
    if not startup_check_run:
        startup_check_run = True
        check_version(bot)


@UnivBot.module.interval(wait_time)
def check_version(bot):
    version = parse_version(UnivBot.__version__)

    info = json.loads(UnivBot.web.get(version_url))
    latest = info['version']
    notes = info['release_notes']
    latest_version = parse_version(latest)

    if version < latest_version:
        bot.msg(bot.config.core.owner,
                message.format(latest, UnivBot.__version__, notes))
