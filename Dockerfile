FROM python:alpine

RUN mkdir /teletorr
COPY telegram_torrent.py /teletorr
COPY transmission.py /teletorr
COPY ya.py /teletorr
COPY pip-requirements.txt /teletorr
RUN pip install --no-cache-dir -r /teletorr/pip-requirements.txt

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

RUN apk add --update git
RUN git clone https://github.com/abbat/ydcmd.git
RUN mv ydcmd/ydcmd.py /usr/local/bin/ydcmd
RUN apk del git pcre

COPY teletorr.sh .
RUN chmod +x teletorr.sh
CMD ["/teletorr.sh"]

