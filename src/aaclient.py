#!/usr/bin/env python3

from bcoding import bencode, bdecode
import hashlib
import time, os
from lxml import html, etree
import requests as re
import libtorrent as lt
import qbittorrentapi


book_xpaths = {
    "collection_div": "//div[contains(@class, 'text-sm') and contains(@class, 'text-gray-500')]",
    "torrent_url": "//div[contains(@class, 'text-sm')]/a[contains(@href, '.torrent')]/@href",
    "torrent_name": "//div[contains(@class, 'text-sm')]/a[contains(@href, '.torrent')]/text()",
    "filename_within_torrent": "//div[contains(@class, 'text-sm')]/text()[contains(., '→') and contains(., 'file')]",
    "extension": "/html/body/main/div/div[1]/div[3]/text()"
}

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
    if fidx == -1:
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

def get_torrent_from_listing(url, save_as, guess_extension, logger):
    try:
        page = re.get(url)
        tree = html.fromstring(page.content)
        
        t_url_elements = tree.xpath(book_xpaths["torrent_url"])
        if not t_url_elements:
            raise ValueError("Torrent URL not found")
        t_url = t_url_elements[0]
        
        torrent_elements = tree.xpath(book_xpaths["torrent_name"])
        if not torrent_elements:
            raise ValueError("Torrent name not found")
        torrent = torrent_elements[0]
        
        filename = tree.xpath(book_xpaths["filename_within_torrent"])[0].split('“', 1)[1][:-1]
        if not filename:
            raise ValueError("Could not extract filename from text")
       
        extension_element = tree.xpath(book_xpaths["extension"])[0].strip()
        extension = [p.strip() for p in extension_element.split('·')][1]

        if guess_extension:
            if extension:
                save_as += f".{extension.lower()}"
        
        aa = url.split("/")
        base_url = f"{aa[0]}//{aa[2]}"
        
        return (f"{base_url}{t_url}", torrent, filename, save_as)
        
    except Exception as e:
        if 'page' in locals():
            logger.warning(f"Page content sample: {page.text[:500]}...")
        raise Exception(f"Error parsing listing page: {e}")

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
        try:
            t_url, torrent, fname, save_as = get_torrent_from_listing(url, save_as, True, self.logger)
            t = re.get(t_url, allow_redirects=True, stream=True)
            path = f"./{torrent}"

            with open(path, "wb") as fout:
                for chunk in t.iter_content(chunk_size=4096):
                    fout.write(chunk)

            return (path, fname, save_as)
        except Exception as e:
            raise Exception(f"Error downloading torrent from listing: {e}")

    def qb_download_torrent(self, t_path, desired_file, save_filename):
        conn_info = dict(
            host=self.qbitt_client["host"],
            port=self.qbitt_client["port"],
            username=self.qbitt_client["username"],
            password=self.qbitt_client["password"],
        )
        qb = None
        is_success = False

        try:
            qb = qbittorrentapi.Client(**conn_info)
            with open(t_path, "rb") as f:
                torrent_data = f.read()
            config = bdecode(torrent_data)
            info = config["info"]

            # Optional: filter out torrents with too many files
            """
            if len(info.get('files', [])) > 1500:
                self.logger.warning(f"Torrent has too many files, skipping: {t_path}")
                return False
            """
            qb.torrents_add(torrent_files=t_path,
                            category=self.qbitt_client.get("musicCategory", None),
                            is_paused=True)
            time.sleep(1)  

            hash_bit = hashlib.sha1(bencode(info)).digest()
            hash = hash_bit.hex()

            files = qb.torrents_files(hash)

            qb.torrents_file_priority(hash, list(range(len(files.data))), priority=0)

            idx = qbitt_file_search(files.data, desired_file)

            qb.torrents_file_priority(hash, idx, 1)

            new_path = os.path.dirname(files[idx].name) + "/" + save_filename
            qb.torrents_rename_file(hash, idx, new_path)

            qb.torrents_start(hash)
            self.logger.info(f"'{save_filename}' added to qBittorrent, downloading only the desired file.")

            is_success = True

        except Exception as e:
            self.logger.error(f"Error adding torrent: {e}\n")
            try:
                if qb:
                    qb.torrents_delete(True, hash)
            except Exception:
                pass  # Ignore deletion errors

        finally:
            if os.path.exists(t_path):
                os.remove(t_path)

        return is_success

    def torrent_from_bookbounty(self, link, save_as, save_path):    
        path, fname, save_as = self.dl_torrent_from_listing(link, save_as)
        
        if self.qbitt_client != None:            
            return self.qb_download_torrent(path, fname, save_as)
        else:
            return self.hnr_download_torrent(path, fname, save_as, save_path)
