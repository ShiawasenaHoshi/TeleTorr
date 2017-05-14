import os

from ya import uploadAndGetLink


class TransmissionAgent:
    def __init__(self, sender, scheduler, token, validUsers, downloadPath, yaDiskToken, transmissionIdPw,
                 transmissionPort):
        self.scheduler = scheduler
        self.TOKEN = token
        self.VALID_USERS = validUsers
        self.DOWNLOAD_PATH = downloadPath
        self.YA_TOKEN = yaDiskToken
        self.TRANSMISSION_ID_PW = transmissionIdPw
        self.TRANSMISSION_PORT = transmissionPort
        self.IDLE = 'Idle'
        self.STATUS_SEED = 'Seeding'
        self.STATUS_ERR = 'Error'  # Need Verification
        self.weightList = {}
        self.sender = sender
        cmd = 'transmission-remote '
        if self.TRANSMISSION_ID_PW:
            cmd = cmd + '-n ' + self.TRANSMISSION_ID_PW + ' '
        else:
            cmd = cmd + '-n ' + 'transmission:transmission' + ' '
        self.transmissionCmd = cmd

        currentList = self.getCurrentList()
        outList = self.parseList(currentList)
        if not self.scheduler.get_jobs() and bool(outList):
            self.scheduler.add_job(self.check_torrents, 'interval', seconds=5)

    def download(self, magnet):
        if self.TRANSMISSION_PORT:
            pcmd = '-p ' + self.TRANSMISSION_PORT + ' '
        else:
            pcmd = ''
        if self.DOWNLOAD_PATH:
            wcmd = '-w ' + self.DOWNLOAD_PATH + ' '
        else:
            wcmd = ''
        os.system(self.transmissionCmd + pcmd + wcmd + '-a ' + magnet)

    def getCurrentList(self):
        l = os.popen(self.transmissionCmd + '-l').read()
        rowList = l.split('\n')
        if len(rowList) < 4:
            return
        else:
            return l

    def start(self, torrents):
        cmd = self.transmissionCmd + '-t ' + torrents + " -s"
        out = os.popen(cmd).read()
        return cmd

    def stop(self, torrents):
        cmd = self.transmissionCmd + '-t ' + torrents + " -S"
        out = os.popen(cmd).read()
        return cmd

    def remove(self, torrents):
        cmd = self.transmissionCmd + '-t ' + torrents + " -r"
        out = os.popen(cmd).read()
        return cmd

    def printElement(self, e):
        outString = 'ID: ' + e['ID'] + \
                    '\nNAME: ' + e['title'] + \
                    '\n' + 'STATUS: ' + e['status'] + '\n'
        outString += 'PROGRESS: ' + e['progress'] + '\n'
        outString += '\n'
        return outString

    def parseList(self, result):
        if not result:
            return
        outList = []
        resultlist = result.split('\n')
        titlelist = resultlist[0]
        resultlist = resultlist[1:-2]
        for entry in resultlist:
            title = entry[titlelist.index('Name'):].strip()
            status = entry[titlelist.index(
                'Status'):titlelist.index('Name') - 1].strip()
            progress = entry[titlelist.index(
                'Done'):titlelist.index('Done') + 4].strip()
            id_ = entry[titlelist.index(
                'ID'):titlelist.index('Done') - 1].strip()
            if id_[-1:] == '*':
                id_ = id_[:-1]
            element = {'title': title, 'status': status,
                       'ID': id_, 'progress': progress}
            outList.append(element)
        return outList

    def removeFromList(self, ID):
        if ID in self.weightList:
            del self.weightList[ID]
        os.system(self.transmissionCmd + '-t ' + ID + ' -r')

    def isOld(self, ID, progress):
        """weightList = {ID:[%,w],..}"""
        if ID in self.weightList:
            if self.weightList[ID][0] == progress:
                self.weightList[ID][1] += 1
            else:
                self.weightList[ID][0] = progress
                self.weightList[ID][1] = 1
            if self.weightList[ID][1] > 3:
                return True
        else:
            self.weightList[ID] = [progress, 1]
            return False
        return False

    def check_torrents(self):
        currentList = self.getCurrentList()
        outList = self.parseList(currentList)
        if not bool(outList):
            self.sender.sendMessage('The torrent List is empty')
            self.scheduler.remove_all_jobs()
            self.weightList.clear()
            return
        for torrent in outList:
            if torrent['status'] == self.STATUS_SEED:
                self.sender.sendMessage(
                    'Download completed: {0}'.format(torrent['title']))
                # todo if document is less than 50mb upload direct to telegram. Other sizes for othe types
                self.upload(torrent)
            elif torrent['status'] == self.STATUS_ERR:
                self.sender.sendMessage(
                    'Download canceled (Error): {0}\n'.format(torrent['title']))
                self.removeFromList(torrent['ID'])
            elif torrent['status'] == self.IDLE and torrent["progress"] == '100%':
                self.sender.sendMessage(
                    'Download completed: {0}'.format(torrent['title']))
                self.upload(torrent)
            else:
                if self.isOld(torrent['ID'], torrent['progress']):
                    self.sender.sendMessage(
                        'Download canceled (pending): {0}\n'.format(torrent['title']))
                    self.upload(torrent)

        return

    def upload(self, torrent):
        try:
            link = uploadAndGetLink(self.DOWNLOAD_PATH, torrent['title'], self.YA_TOKEN)
            self.sender.sendMessage(torrent['title'] + " uploaded to yandex. Link: " + link)
            self.removeFromList(torrent['ID'])
            self.delete_file_from_storage(torrent['ID'])
        except Exception as e:
            self.sender.sendMessage('Uploading ERROR: {0}'.format(e))
        # todo print freespace in yadisk
        # todo if file uploaded then delete it
        # todo link too long

    def delete_file_from_storage(self, fileName):
        if os.path.exists(self.DOWNLOAD_PATH + fileName):
            os.remove(self.DOWNLOAD_PATH + fileName)
            # todo and for dirs
