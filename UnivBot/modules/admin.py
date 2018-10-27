# coding=utf8
"""
admin.py - UnivBot Admin Module
Copyright 2010-2011, Sean B. Palmer (inamidst.com) and Michael Yanovich
(yanovich.net)
Copyright © 2012, Elad Alfassa, <elad@fedoraproject.org>
Copyright 2013, Ari Koivula <ari@koivu.la>

Licensed under the Eiffel Forum License 2.

http://UnivBot.dftba.net
"""
from __future__ import unicode_literals

import UnivBot.module


def configure(config):
    """
    | [admin] | example | purpose |
    | -------- | ------- | ------- |
    | hold_ground | False | Auto re-join on kick |
    """
    config.add_option('admin', 'hold_ground', "Auto re-join on kick")


@UnivBot.module.commands('join')
@UnivBot.module.priority('low')
@UnivBot.module.example('%join #ejemplo o %join #ejemplo contraseña')
def join(bot, trigger):
    """Entra al canal especificado el bot. Solo para uso de los admin del bot por mensaje privado."""
    # Can only be done in privmsg by an admin
    if not trigger.is_privmsg:
        return

    if trigger.admin:
        channel, key = trigger.group(3), trigger.group(4)
        if not channel:
            return
        elif not key:
            bot.join(channel)
        else:
            bot.join(channel, key)


@UnivBot.module.commands('part')
@UnivBot.module.priority('low')
@UnivBot.module.example('%part #ejemplo')
def part(bot, trigger):
    """Sale del canal especificado. Solo para uso de los admin del bot por mensaje privado."""
    # Can only be done in privmsg by an admin
    if not trigger.is_privmsg:
        return
    if not trigger.admin:
        return

    channel, _sep, part_msg = trigger.group(2).partition(' ')
    if part_msg:
        bot.part(channel, part_msg)
    else:
        bot.part(channel)


@UnivBot.module.commands('quit')
@UnivBot.module.priority('low')
def quit(bot, trigger):
    """Sale del servidor actual. Solo puede ser ejecutado por el owner del bot por mensaje privado."""
    # Can only be done in privmsg by the owner
    if not trigger.is_privmsg:
        return
    if not trigger.owner:
        return

    quit_message = trigger.group(2)
    if not quit_message:
        quit_message = '[Shutdown] Solicitado por %s' % trigger.nick

    bot.quit(quit_message)


@UnivBot.module.commands('msg')
@UnivBot.module.priority('low')
@UnivBot.module.example('%msg #Wikipedia Buenos días')
def msg(bot, trigger):
    """
    Envía un mensaje al canal o usuario especificado. Solo para uso de los admin por mensaje privado.
    """
    if not trigger.is_privmsg:
        return
    if not trigger.admin:
        return
    if trigger.group(2) is None:
        return

    channel, _sep, message = trigger.group(2).partition(' ')
    message = message.strip()
    if not channel or not message:
        return

    bot.msg(channel, message)


@UnivBot.module.commands('me')
@UnivBot.module.priority('low')
def me(bot, trigger):
    """
    Envía una acción al canal especificado. Solo para uso de los admin por mensaje privado.
    """
    if not trigger.is_privmsg:
        return
    if not trigger.admin:
        return
    if trigger.group(2) is None:
        return

    channel, _sep, action = trigger.group(2).partition(' ')
    action = action.strip()
    if not channel or not action:
        return

    msg = '\x01ACTION %s\x01' % action
    bot.msg(channel, msg)


@UnivBot.module.event('INVITE')
@UnivBot.module.rule('.*')
@UnivBot.module.priority('low')
def invite_join(bot, trigger):
    """
    Entra a un canal cuando el bot sea invitado. Solo para uso de los admin.
    """
    if not trigger.admin:
        return
    bot.join(trigger.args[1])


@UnivBot.module.event('KICK')
@UnivBot.module.rule(r'.*')
@UnivBot.module.priority('low')
def hold_ground(bot, trigger):
    """
    This function monitors all kicks across all channels UnivBot is in. If it
    detects that it is the one kicked it'll automatically join that channel.

    WARNING: This may not be needed and could cause problems if UnivBot becomes
    annoying. Please use this with caution.
    """
    if bot.config.has_section('admin') and bot.config.admin.hold_ground:
        channel = trigger.sender
        if trigger.args[1] == bot.nick:
            bot.join(channel)


@UnivBot.module.commands('mode')
@UnivBot.module.priority('low')
def mode(bot, trigger):
    """Establece un modo de usuario al Bot. Solo para uso de los admin por mensaje privado."""
    if not trigger.is_privmsg:
        return
    if not trigger.admin:
        return
    mode = trigger.group(3)
    bot.write(('MODE ', bot.nick + ' ' + mode))


@UnivBot.module.commands('set')
@UnivBot.module.example('.set core.owner Me')
def set_config(bot, trigger):
    """Muestra y modifica parámetros del bot.
       Solo para uso de los admin por mensaje privado.

    Argumentos:
        arg1 - sección y opción en el formato "section.option"
        arg2 - valor

    Si no se especifica una sección se toma "core" por defecto.
    Si no se le asigna un valor, se elimina la opción.
    """
    if not trigger.is_privmsg:
        bot.reply("Solo puede ser ejecutado en un mensaje privado..")
        return
    if not trigger.admin:
        bot.reply("Necesitas tener privilegios de admin del bot.")
        return

    # Get section and option from first argument.
    arg1 = trigger.group(3).split('.')
    if len(arg1) == 1:
        section, option = "core", arg1[0]
    elif len(arg1) == 2:
        section, option = arg1
    else:
        bot.reply("Uso: %set section.option value")
        return

    # Display current value if no value is given.
    value = trigger.group(4)
    if not value:
        if not bot.config.has_option(section, option):
            bot.reply("La opción %s.%s no existe." % (section, option))
            return
        # Except if the option looks like a password. Censor those to stop them
        # from being put on log files.
        if option.endswith("password") or option.endswith("pass"):
            value = "(contraseña censurada)"
        else:
            value = getattr(getattr(bot.config, section), option)
        bot.reply("%s.%s = %s" % (section, option, value))
        return

    # Otherwise, set the value to one given as argument 2.
    setattr(getattr(bot.config, section), option, value)


@UnivBot.module.commands('save')
@UnivBot.module.example('.save')
def save_config(bot, trigger):
    """Guarda el estado de la configuración de DreamBot en el archivo de configuración."""
    if not trigger.is_privmsg:
        return
    if not trigger.admin:
        return
    bot.config.save()
