FROM python:alpine

COPY yadisk /teletorr/yadisk
COPY setting.json /teletorr
COPY transmission.py /teletorr
COPY ya.py /teletorr
COPY telegram_torrent.py /teletorr
COPY pip-requirements.txt /teletorr
RUN pip install --no-cache-dir -r  /teletorr/pip-requirements.txt

RUN sudo echo "America/New_York" > /etc/timezone
RUN sudo dpkg-reconfigure -f noninteractive tzdata

#thanks to https://github.com/rlesouef for dockerized transmission
COPY docker_transmission/ .
RUN apk add --update \
    transmission-daemon \
    transmission-cli \
    && rm -rf /var/cache/apk/*
RUN mkdir -p /transmission/downloads \
    && mkdir -p /transmission/incomplete \
    && mkdir -p /etc/transmission-daemon
VOLUME ["/transmission/downloads"]
VOLUME ["/transmission/incomplete"]

COPY teletorr.sh .
RUN chmod +x teletorr.sh
CMD ["/teletorr.sh"]

