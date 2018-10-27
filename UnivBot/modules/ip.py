# coding=utf8
"""
ip.py - Vortexz IP Lookup Module
Copyright © 2018 Freuddy
Licensed under the Eiffel Forum License 2.

http://UnivBot.dftba.net
"""
from __future__ import unicode_literals

import re
import pygeoip
import socket
import os
import gzip

urlretrieve = None
try:
    from urllib import urlretrieve
except ImportError:
    try:
        # urlretrieve has been put under urllib.request in Python 3.
        # It's also deprecated so this should probably be replaced with
        # urllib2.
        from urllib.request import urlretrieve
    except ImportError:
        pass

from UnivBot.module import commands, example


def configure(config):
    """

    | [ip] | example | purpose |
    | ---- | ------- | ------- |
    | GeoIP_db_path | None | Full path for the GeoIP database. If not specified or None, the bot will try to look for the database in /usr/share/GeoIP, and if it's not there it'll try to automatically download the database into its configuration directory |
    """
    if config.option('Configure a custom location for the GeoIP db?', False):
        config.add_section('ip')
        config.interactive_add('ip', 'GeoIP_db_path', 'Full path to the GeoIP database', None)


def _decompress(source, target, delete_after_decompression=True):
    """ Decompress a GZip file """
    f_in = gzip.open(source, 'rb')
    f_out = open(target, 'wb')
    f_out.writelines(f_in)
    f_out.close()
    f_in.close()
    if delete_after_decompression:
        os.remove(source)


def _find_geoip_db(bot):
    """ Find the GeoIP database """
    config = bot.config
    if config.has_section('ip') and config.ip.GeoIP_db_path is not None:
        cities_db = os.path.join(config.ip.GeoIP_db_path, 'GeoLiteCity.dat')
        ipasnum_db = os.path.join(config.ip.GeoIP_db_path, 'GeoIPASNum.dat')
        if os.path.isfile(cities_db) and os.path.isfile(ipasnum_db):
            return config.ip.GeoIP_db_path
        else:
            bot.debug(__file__, 'GeoIP path configured but DB not found in configured path', 'warning')
    if (os.path.isfile(os.path.join(bot.config.homedir, 'GeoLiteCity.dat')) and
            os.path.isfile(os.path.join(bot.config.homedir, 'GeoIPASNum.dat'))):
        return bot.config.homedir
    elif (os.path.isfile(os.path.join('/usr/share/GeoIP', 'GeoLiteCity.dat')) and
            os.path.isfile(os.path.join('/usr/share/GeoIP', 'GeoIPASNum.dat'))):
        return '/usr/share/GeoIP'
    elif urlretrieve:
        bot.debug(__file__, 'Downloading GeoIP database', 'always')
        bot.say('Descargando la base de datos de GeoIP, por favor espera...')
        geolite_city_url = 'http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz'
        geolite_ASN_url = 'http://download.maxmind.com/download/geoip/database/asnum/GeoIPASNum.dat.gz'
        geolite_city_filepath = os.path.join(bot.config.homedir, 'GeoLiteCity.dat.gz')
        geolite_ASN_filepath = os.path.join(bot.config.homedir, 'GeoIPASNum.dat.gz')
        urlretrieve(geolite_city_url, geolite_city_filepath)
        urlretrieve(geolite_ASN_url, geolite_ASN_filepath)
        _decompress(geolite_city_filepath, geolite_city_filepath[:-3])
        _decompress(geolite_ASN_filepath, geolite_ASN_filepath[:-3])
        return bot.config.homedir
    else:
        return False


@commands('iplookup', 'ip')
@example('%ip 8.8.8.8',
        r'[IP/Host Lookup] Hostname: google-public-dns-a.google.com | Location: United States | ISP: Google Inc.',
        re=True, 
        ignore='Downloading GeoIP database, please wait...')
def ip(bot, trigger):
    """Herramienta de geolocalización de IPs"""
    if not trigger.group(2):
        return bot.reply("No hay nada a buscar.")
    query = trigger.group(2)
    db_path = _find_geoip_db(bot)
    if db_path is False:
        bot.debug(__file__, 'No se pudo encontrar una base de datos para esta IP', 'always')
        bot.say('Lo siento, no se pudo encontrar una base de datos para esta IP')
        return False
    geolite_city_filepath = os.path.join(_find_geoip_db(bot), 'GeoLiteCity.dat')
    geolite_ASN_filepath = os.path.join(_find_geoip_db(bot), 'GeoIPASNum.dat')
    gi_city = pygeoip.GeoIP(geolite_city_filepath)
    gi_org = pygeoip.GeoIP(geolite_ASN_filepath)
    host = socket.getfqdn(query)
    response = "[Geolocalización IP/Host] Nombre del host: %s" % host
    response += " | Ubicación: %s" % gi_city.country_name_by_name(query)
    
    region_data = gi_city.region_by_name(query)
    try:
        region = region_data['region_code']  # pygeoip >= 0.3.0
    except KeyError:
        region = region_data['region_name']  # pygeoip < 0.3.0
    if region:
        response += " | Región: %s" % region
    
    isp = gi_org.org_by_name(query)
    if isp is not None:
        isp = re.sub('^AS\d+ ', '', isp)
    response += " | ISP: %s" % isp
    bot.say(response)


if __name__ == "__main__":
    from UnivBot.test_tools import run_example_tests
    run_example_tests(__file__)
