#UnivBot

This folder contains UnivBot.service and UnivBot.cfg designed to be distributed by 3rd party distrubtions such as Fedora Project or Arch Linux.

UnivBot.cfg is a default configuration file for UnivBot, that assumes the OS is new enough to have /run and /usr/lib/tmpfiles.d

UnivBot.service is a systemd service file that assumes you are using a rather recent UnivBot and has no multiple instance support (TODO). It also assumes that the system has a special user named UnivBot designated for running the bot and this user has access to /run/UnivBot (should be setup by UnivBot.conf in /usr/lib/tmpfiles.d), /var/log/UnivBot and /var/lib/UnivBot

Default installation paths:
 UnivBot.cfg	/etc
 UnivBot.conf	/usr/lib/tmpfiles.d
 UnivBot.service	/usr/lib/systemd/system
