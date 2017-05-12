from yadisk.YandexDiskRestClient import YandexDiskRestClient


def uploadAndGetLink(path, filename, token):
    #todo recursive upload folders
    client = YandexDiskRestClient(token)
    try:
        link = client.get_download_link_to_file("/" + filename)
    except:
        client.upload_file(path + "/" + filename, "/" + filename)
        link = client.get_download_link_to_file("/" + filename)
    return link