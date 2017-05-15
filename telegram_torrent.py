#!/usr/bin/python3
import json
import os
import random
import string
from urllib import parse

import feedparser
import telepot
from apscheduler.schedulers.background import BackgroundScheduler
from telepot.delegate import per_chat_id, create_open, pave_event_space

from transmission import TransmissionAgent

CONFIG_FILE = 'setting.json'


class Torrenter(telepot.helper.ChatHandler):
    rssUrl = """https://torrentkim1.net/bbs/rss.php?k="""

    global scheduler
    DownloadFolder = ''  # Option: Input your subtitle location to save subtitle files,

    mode = ''
    navi = feedparser.FeedParserDict()

    def __init__(self, *args, **kwargs):
        super(Torrenter, self).__init__(*args, **kwargs)
        self.agent = TransmissionAgent(self.sender, scheduler, token, validUsers, downloadPath, yaDiskToken)

    def open(self, initial_msg, seed):
        self.menu()

    def on_close(self, exception):
        pass

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        # Check ID
        if not chat_id in validUsers:
            print("Permission Denied")
            return

        if content_type is 'text':
            self.handle_command(msg['text'])
            return

        if content_type is 'document':
            file_name = msg['document']['file_name']
            if file_name[-7:] == 'torrent':
                file_id = msg['document']['file_id']
                self.handle_seedfile(file_id)
                return
            self.sender.sendMessage('Invalid File')
            return

        self.sender.sendMessage('Invalid File')

    def handle_command(self, command):
        if command == self.MENU_HOME:
            self.menu()
        elif command == self.MENU_SEARCH:
            self.tor_get_keyword()
        elif command == self.MENU_TORRENT_LIST:
            self.tor_show_list()
        elif self.mode == self.MENU_INPUT_WORD:  # Get Keyword
            self.tor_search(command)
        elif self.mode == self.MENU_CHOOSE_TORRENT:
            self.tor_download(command)
        elif self.mode == self.MENU_TORRENT_LIST and command == self.MENU_MAN_CMD:
            self.tor_help()
        elif self.mode == self.MENU_TORRENT_LIST and command.lower().startswith("/"):
            self.tor_list_cmd(command)

    def handle_seedfile(self, file_id):
        try:
            self.sender.sendMessage('Saving torrent file..')
            generated_file_path = self.DownloadFolder + \
                                  "".join(random.sample(string.ascii_letters, 8)) + ".torrent"
            bot.download_file(file_id, generated_file_path)
            self.agent.download(generated_file_path)
            os.system("rm " + generated_file_path)
            if not scheduler.get_jobs():
                scheduler.add_job(self.agent.check_torrents,
                                  'interval', minutes=1)
        except Exception as inst:
            self.sender.sendMessage('ERORR: {0}'.format(inst))
            return
        self.sender.sendMessage('Start Downloading')  # todo send filename

    # ---------- Concrete commands ------------
    GREETING = "Select menu"
    MENU_HOME = 'Home'
    MENU_SEARCH = 'Search torrent'
    MENU_INPUT_WORD = 'Type a word'
    MENU_CHOOSE_TORRENT = 'Choose an item'
    MENU_TORRENT_LIST = 'Torrent list'
    MENU_MAN_CMD = "Help"
    MENU_START = '/st'
    MENU_STOP = '/sp'
    MENU_REMOVE = '/rm'

    def menu(self):
        mode = ''
        show_keyboard = {'keyboard': [
            [self.MENU_SEARCH], [self.MENU_TORRENT_LIST], [self.MENU_HOME]]}
        self.sender.sendMessage(self.GREETING, reply_markup=show_keyboard)

    def tor_get_keyword(self):
        self.mode = self.MENU_INPUT_WORD
        self.sender.sendMessage('Enter a Keyword')

    def tor_show_list(self):
        self.mode = self.MENU_TORRENT_LIST
        result = self.agent.getCurrentList()
        if not result:
            self.sender.sendMessage('The torrent list is empty')
            self.menu()
            return
        outList = self.agent.parseList(result)
        for e in outList:
            self.sender.sendMessage(self.agent.printElement(e))

        if outList.__len__() > 0:
            show_keyboard = {'keyboard': [
                [self.MENU_SEARCH], [self.MENU_TORRENT_LIST], [self.MENU_MAN_CMD], [self.MENU_HOME]]}
            self.sender.sendMessage(self.GREETING, reply_markup=show_keyboard)

    def tor_search(self, keyword):
        self.mode = ''
        self.sender.sendMessage('Searching torrent..')
        self.navi = feedparser.parse(self.rssUrl + parse.quote(keyword))

        outList = []
        if not self.navi.entries:
            self.sender.sendMessage('Sorry, No results')
            self.mode = self.MENU_INPUT_WORD
            return

        for (i, entry) in enumerate(self.navi.entries):
            if i == 10:
                break
            title = str(i + 1) + ". " + entry.title

            templist = []
            templist.append(title)
            outList.append(templist)

        show_keyboard = {'keyboard': self.put_menu_button(outList)}
        self.sender.sendMessage('Choose one from below',
                                reply_markup=show_keyboard)
        self.mode = self.MENU_CHOOSE_TORRENT

    def put_menu_button(self, l):
        menulist = [self.MENU_HOME]
        l.append(menulist)
        return l

    def tor_download(self, selected):
        self.mode = ''
        index = int(selected.split('.')[0]) - 1
        magnet = self.navi.entries[index].link
        self.agent.download(magnet)
        self.sender.sendMessage('Start Downloading')
        self.navi.clear()
        if not scheduler.get_jobs():
            scheduler.add_job(self.agent.check_torrents, 'interval', seconds=5)
        self.menu()

    def tor_help(self):
        show_keyboard = {'keyboard': [
            [self.MENU_SEARCH], [self.MENU_TORRENT_LIST], [self.MENU_MAN_CMD], [self.MENU_HOME]]}
        self.sender.sendMessage("Commands:\n"
                                "/st 1 - start torrent with id 1\n"
                                "/sp 2,3 - stop torrents with id 2 and 3\n"
                                "/rm all - remove all torrents", reply_markup=show_keyboard)

    def tor_list_cmd(self, cmd):
        cmd = cmd.lower()
        if cmd.startswith(self.MENU_START.lower()):
            self.agent.start(cmd.replace(self.MENU_START.lower() + " ", ""))
        elif cmd.startswith(self.MENU_STOP.lower()):
            self.agent.stop(cmd.replace(self.MENU_STOP.lower() + " ", ""))
        elif cmd.startswith(self.MENU_REMOVE.lower()):
            self.agent.remove(cmd.replace(self.MENU_REMOVE.lower() + " ", ""))
        self.tor_show_list()


def parseConfig(filename):
    path = os.path.dirname(os.path.realpath(__file__)) + '/' + filename
    f = open(path, 'r')
    js = json.loads(f.read())
    f.close()
    return js


def getConfig(config):
    global token
    global AGENT_TYPE
    global validUsers
    global downloadPath
    global yaDiskToken
    token = config['common']['token']
    validUsers = config['common']['valid_users']
    downloadPath = config['common']['download_path']
    yaDiskToken = config["yadisk"]['token']


config = parseConfig(CONFIG_FILE)
if not bool(config):
    print("Err: Setting file is not found")
    exit()
getConfig(config)
scheduler = BackgroundScheduler()
scheduler.start()
bot = telepot.DelegatorBot(token, [
    pave_event_space()(
        per_chat_id(), create_open, Torrenter, timeout=120),
])
bot.message_loop(run_forever='Listening ...')
