import os


def uploadAndGetLink(path, filename, token):
    UPLOAD_CMD = 'ydcmd put \'{path}/{filename}\' \'disk:/{uploadpath}\' --token={token}'
    SHARE_CMD = "ydcmd share \'disk:/{filename}\' --token={token}"
    # todo specify upload folder
    try:
        os.system(UPLOAD_CMD.format(path=path, filename=filename, uploadpath='', token=token))
        link = os.popen(SHARE_CMD.format(filename=filename, token=token)).read()
        return link
    except Exception as e:
        return e
