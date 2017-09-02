# TeleTorr
The Telegram Bot can control a Transmission torrent client
- searching
- download
- control of downloads
- autoexport to yandex disk

TeleTorr live in docker container

## How to Use Docker container
### 1) Install docker and create neccessary folders 
- for finished downloads e.g. /path/to/torrents/downloads
- for incomplete downloads e.g. /path/to/torrents/incomplete

### 2) Write setting.json
```json
{
  "common": {
    "token": "110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw",
    "valid_users": [
      123456789,
      123456789
    ],
    "download_path": "/transmission/downloads"
  },
  "yadisk":{
    "token":"AQAAWAAYFkjxAACCgFQP4DhRH0W-i9tBuGmrU_E"
  }
}
```
* token: The token is a string along the lines of 110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw that will be required to authorize the bot and send requests to the Bot API. Use this bot https://telegram.me/BotFather
* valid_users: The user that is list up in valid_users can communicate with the telegram bot.
Every Telegram user has own id string. put your telegram id into that. You can get user_id through special bot e.g. https://telegram.me/ShowJsonBot
* yadisk: The token of yandex API for working with yandex disk. How to get token - https://github.com/abbat/ydcmd

### 3) Start container
sudo docker run -it --rm --name teletorr \\\
-v /etc/timezone:/etc/timezone:ro \\\
-v /path/to/setting.json:/teletorr/setting.json:ro \\\
-v /path/to/torrents/downloads:/transmission/downloads \\\
-v /path/to/torrents/incomplete:/transmission/incomplete \\\
shiawasenahoshi/teletorr

## Thanks to:
**seungjuchoi** for telegram-control-torrent which I forked\
**abbat** for ydcmd - yandex disk console client\
**rlesouef** for dockerized transmission
