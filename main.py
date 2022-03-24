# -*- coding: utf-8 -*-
import os
import re

import aria2p
import feedparser
import requests
import yaml

MAX_HISTORY = 300

workspace = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(workspace, 'config', 'config.yml')
history_path = os.path.join(workspace, 'config', 'history.txt')

torrents_save_dir = os.path.join(workspace, 'torrents')
if not os.path.exists(torrents_save_dir):
    os.makedirs(torrents_save_dir)


def load_config():
    if os.path.exists(config_path):
        return yaml.safe_load(open(config_path, encoding='utf8'))
    else:
        raise RuntimeError('config not found!')


config = load_config()

MAX_HISTORY = max(MAX_HISTORY, len(list(filter(lambda d:d.get('enable',True),config.get('mikan', [])))) * 48)


def load_history():
    h = set()
    if os.path.exists(history_path):
        with open(history_path, encoding='utf8') as f:
            for line in f:
                bang = line.strip()
                if bang == '':
                    continue
                h.add(bang)
                if len(h) >= MAX_HISTORY:
                    break
    else:
        w = open(history_path, 'w')
        w.close()
    return h


downloaded_history = load_history()

cache = []

agent = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.62"}

client = aria2p.API(aria2p.Client(**config['aria2']))
base_dir = client.get_global_options().get('dir')

session = requests.session()
if config.get('proxy'):
    session.proxies = config['proxy']
session.headers = agent


def aria2(url, dir):
    if url.startswith("magnet:?xt="):
        client.add_magnet(url, options={'dir': f'{base_dir}/{dir}'})
    else:
        _, filename = os.path.split(url)
        filename = os.path.join(torrents_save_dir, filename)
        if not os.path.exists(filename):
            resp = session.get(url)
            with open(filename, 'wb') as w:
                w.write(resp.content)
        client.add_torrent(filename, options={'dir': f'{base_dir}/{dir}'})


def get_latest(url, rule=None, savedir=None):
    bangumi_cache = set()
    content = session.get(url).content
    entries = feedparser.parse(content)
    if savedir:
        bangumi_name = savedir
    else:
        bangumi_name = entries['feed']['title'][16:]
    for entry in entries['entries']:
        title = entry['title'].strip()
        if rule:
            if not re.search(rule, title):
                continue
        if title not in downloaded_history and title not in bangumi_cache:
            download_url = None
            for link in entry['links']:
                if link['type'] == 'application/x-bittorrent':
                    download_url = link['href']
            if download_url:
                aria2(download_url, bangumi_name)
                bangumi_cache.add(title)
                cache.append(title)
        else:
            continue
    downloaded_history.update(bangumi_cache)


def write_history(line):
    """把最新的历史写在最前方"""
    line = line.strip()
    if line == '':
        return
    with open(history_path, 'r+', encoding='utf8') as w:
        content = w.read()
        w.seek(0, 0)
        w.write(line + '\n' + content)


def run():
    for bangumi in config['mikan']:
        url = bangumi['url']
        rule = bangumi.get('rule')
        enable = bangumi.get('enable', True)
        if not enable:
            continue
        if rule == '':
            rule = None
        savedir = bangumi.get('savedir')
        if savedir == '':
            savedir = None
        get_latest(url, rule=rule, savedir=savedir)
    if len(cache) > 0:
        write_history('\n'.join(cache[::-1]))


if __name__ == '__main__':
    run()
