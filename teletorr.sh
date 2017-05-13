#!/bin/sh
transmission-daemon --no-auth --config-dir /etc/transmission-daemon
python /teletorr/telegram_torrent.py
