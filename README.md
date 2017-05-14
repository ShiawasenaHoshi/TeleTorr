# Teletorr
The Telegram Bot can control a Transmission torrent client
- searching
- download
- control of downloads
- autoexport to yandex disk

Teletorr live in docker container

## How to Use
### 1) Write setting.json
```json
{
  "common": {
    "token": "110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw",
    "valid_users": [
      123456789,
      123456789
    ],
    "agent_type": "transmission",
    "download_path": "~/Downloads"
  },
  "transmission": {
    "id_pw": "transmission:transmission",
    "port": ""
  },
  "yadisk":{
    "token":"AQAAWAAYFkjxAACCgFQP4DhRH0W-i9tBuGmrU_E"
  }
}
```
* token: The token is a string along the lines of 110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw that will be required to authorize the bot and send requests to the Bot API.
* valid_users: The user that is list up in valid_users can communicate with the telegram bot.
Every Telegram user has own id string. put your telegram id into that
* yadisk: The token of yandex API for working with yandex disk

### 2) Start container
sudo docker run -it --rm --name teletorr \\\
-v /etc/timezone:/etc/timezone:ro \\\
-v /path/to/setting.json:/teletorr/setting.json:ro \\\
-v /path/to/torrents/downloads:/torrents/downloads \\\
-v /path/to/torrents/incomplete:/torrents/incomplete \\\
shiawasenahoshi/teletorr

## Thanks to:
**seungjuchoi** for telegram-control-torrent which I forked\
**abbat** for simple ydcmd - yandex disk console client\
**rlesouef** for dockerized transmission
