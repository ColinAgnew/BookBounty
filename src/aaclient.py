#!/usr/bin/env python3

from bcoding import bencode, bdecode
import hashlib
import time, os
from lxml import html, etree
import requests as re
import libtorrent as lt
import qbittorrentapi


book_xpaths = {"collection": "/html/body/main/div[3]/ul/li[last()]/div/a[1]",
               "torrent": "/html/body/main/div[3]/ul/li[last()]/div/a[2]/text()",
               "torrent_url": "/html/body/main/div[3]/ul/li[last()]/div/a[2]/@href",
               "filename_within_torrent": "/html/body/main/div[3]/ul/li[last()]/div/text()[3]",
               "title": "/html/body/main/div[1]/div[3]/text()",
               "extension": "/html/body/main/div[1]/div[2]/text()"}

replace_chars = str.maketrans(dict.fromkeys(''.join([" /"]), '.') | dict.fromkeys(''.join([":;"]), None))

state_str = ['queued', 'checking', 'downloading metadata', \
    'downloading', 'finished', 'seeding', 'allocating', 'checking fastresume']

def file_search(torrent_info, desired_file):
    priorities = []
    fidx = -1
    size = -1
    path = ""
    for idx, des in enumerate(torrent_info.files()):
        if des.path.endswith(desired_file):
            priorities.append(255)
            fidx = idx
            size = des.size
            path = des.path # todo: tidy this up a bit
        else:
            priorities.append(0)
    if idx == -1:
        raise Exception("Destination file not found in torrent")
    return (fidx, size, path, priorities)

def check_torrent_completion(ses, idx):

    alerts = ses.pop_alerts()

    for a in alerts:
        alert_type = type(a).__name__
        if alert_type == "file_completed_alert":
            if a.index == idx:
                return True

    return False

def get_torrent_from_listing(url, save_as, guess_extension):
    page = re.get(url)
    tree = html.fromstring(page.content)

    fname = tree.xpath(book_xpaths["filename_within_torrent"])[0].split('“', 1)[1][:-1]
    t_url = tree.xpath(book_xpaths["torrent_url"])[0]
    torrent = tree.xpath(book_xpaths["torrent"])[0][:-1][1:]

    extension = tree.xpath(book_xpaths["extension"])[0].split(', ')[1]

    if guess_extension:
        save_as += extension
    aa = url.split("/")
    return (f"{aa[0]}//{aa[2]}{str(t_url)}", torrent, fname, save_as)

def qbitt_file_search(torrent_files, desired_file):
    for idx, des in enumerate(torrent_files):
        if des["name"].endswith(desired_file):
            return idx            
    
    raise Exception("Destination file not found in torrent")


class aaclient:
    def __init__(self, logger, qbitt_client = None):
        self.logger = logger 
        self.qbitt_client = qbitt_client    
    
    def hnr_download_torrent(self, t_path, desired_file, save_filename, save_path):
        info = lt.torrent_info(t_path)
        ses = lt.session({'listen_interfaces': '0.0.0.0:6881'})

        idx, size, path, priorities = file_search(info, desired_file)

        h = ses.add_torrent({'ti': info, 'save_path': save_path})
        h.prioritize_files(priorities)

        alert_mask = (lt.alert.category_t.error_notification |
                            lt.alert.category_t.performance_warning |
                            lt.alert.category_t.progress_notification)
        ses.set_alert_mask(alert_mask)
        
        self.logger.info(f"Downloading: {save_filename} - Size: {size/1048576:.2f} MB")
        os.remove(t_path)
        while True:
            s = h.status()
            prog = h.file_progress()[idx]
            self.logger.info(f"{prog} - {state_str[s.state]} ({s.num_peers} {'peer' if s.num_peers == 1 else 'peers'})")

            if check_torrent_completion(ses, idx):
                os.rename(save_path + "/" + path, save_path + "/" + save_filename)
                return True

            time.sleep(10)


    def dl_torrent_from_listing(self, url, save_as):
        self.logger.info(f"Getting torrent listing from: {url}")
        t_url, torrent, fname, save_as = get_torrent_from_listing(url, save_as, True)
        t = re.get(t_url, allow_redirects=True, stream=True)
        path = f"./{torrent}"

        with open(path, "wb") as fout:
            self.logger.info(f"Downloading {torrent}")
            for chunk in t.iter_content(chunk_size=4096):
                fout.write(chunk)
            self.logger.info(f"Downloaded {torrent}")

        return (path, fname, save_as)


    def qb_download_torrent(self, t_path, desired_file, save_filename):
        conn_info = dict(
            host=self.qbitt_client["host"],
            port=self.qbitt_client["port"],
            username=self.qbitt_client["username"],
            password=self.qbitt_client["password"],
        )
        
        with open(t_path, "rb") as f:
            torrent_data = f.read()
        config = bdecode(torrent_data)
        info = config["info"]
        hash_bit = hashlib.sha1(bencode(info)).digest()
        hash = hash_bit.hex()
            
        if len(info['files']) > 1500:
            self.logger.error(f"This torrent has too much stuff, I don't want it. {t_path} not added to qBittorrent")
            os.remove(t_path) 
            return False
                
        qb = qbittorrentapi.Client(**conn_info)        
        qb.torrents_add(torrent_files=t_path, category=self.qbitt_client["musicCategory"], is_paused=True)
        time.sleep(1) # allow metadata to be downloaded
        os.remove(t_path)
        
        files = qb.torrents_files(hash)    
        qb.torrents_file_priority(hash, [i for i in range(len(files))], priority=0) # Do not download   
        
        try:
            idx = qbitt_file_search(files.data, desired_file)   
            qb.torrents_file_priority(hash, idx, 1) # Normal dl
            new_path = os.path.dirname(files[idx].name) + "/" +  save_filename
            qb.torrents_rename_file(hash, idx, new_path)
            qb.torrents_start(hash)        
            self.logger.info(f"{save_filename} added to qBittorrent")
            return True       
        except:
            qb.torrents_delete(True, hash)        
            self.logger.error(f"Error adding book. {t_path} removed from qBittorrent")  
        
        return False
        
    def torrent_from_bookbounty(self, link, save_as, save_path):    
        path, fname, save_as = self.dl_torrent_from_listing(link, save_as)
        
        if self.qbitt_client != None:            
            return self.qb_download_torrent(path, fname, save_as)
        else:
            return self.hnr_download_torrent(path, fname, save_as, save_path)
            
