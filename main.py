# -*- coding: utf-8 -*-
import os
import re

import aria2p
import feedparser
import requests
from pathlib import Path
from loguru import logger

workspace = Path(os.path.realpath(__file__)).parent

if env_config_path := os.getenv("MTA_CONFIGPATH"):
    logger.info(f"load config from env, {env_config_path}")
    config_path = Path(env_config_path)
else:
    logger.info("use default config path, config/config.yml")
    config_path = workspace.joinpath("config", "config.yml")

config = None
if config_path.exists() and config_path.is_file():
    if config_path.suffix in (".yml", ".yaml"):
        import yaml

        config = yaml.safe_load(config_path.open(encoding="utf8"))
    elif config_path.suffix == '.json':
        import json

        config = json.load(config_path.open(encoding="utf8"))
    else:
        logger.warning(f"unsupported config file, {config_path.name}")
if not config:
    logger.error("config not found!")
    exit(1)

if history_path := os.getenv("MTA_HISTORY_FILE"):
    history_path = Path(history_path)
else:
    history_path = workspace.joinpath("config", "history.txt")
logger.info(f"use history file: {history_path.as_posix()}")
history_path.parent.mkdir(parents=True, exist_ok=True)

if torrent_dir := os.getenv("MTA_TORRENTS_DIR"):
    torrents_save_dir = Path(torrent_dir)
else:
    torrents_save_dir = workspace.joinpath("torrents")
logger.info(f"us torrent dir: {torrents_save_dir.as_posix()}")
torrents_save_dir.parent.mkdir(parents=True, exist_ok=True)

MAX_HISTORY = os.getenv("MTA_MAX_HISTORY", max(300, len([filter(lambda d: d.get('enable', True), config.get('mikan', []))]) * 48))
logger.info(f"max history size, set to {MAX_HISTORY}")

def load_history() -> set:
    history = set()
    if history_path.exists() and history_path.is_file():
        with history_path.open(encoding='utf8') as f:
            for line in f:
                bang = line.strip()
                if bang == '':
                    continue
                history.add(bang)
                if len(history) >= MAX_HISTORY:
                    break
    else:
        history_path.touch(exist_ok=True)
    return history


downloaded_history = load_history()

cache = []

if "aria2" in config:
    client = aria2p.API(aria2p.Client(**config['aria2']))
else:
    client = None
    if host := os.getenv("MTA_ARIA2_HOST"):
        if port := os.getenv("MTA_ARIA2_PORT"):
            client = aria2p.API(aria2p.Client(host=host, port=int(port), secret=os.getenv("MTA_ARIA2_SECRET", "")))
if not client:
    logger.error("aria2 not set!")
    exit(1)

from requests.exceptions import ConnectionError

try:
    ARIA2_BASE_DIR = client.get_global_options().get('dir')
except ConnectionError:
    logger.error("aria2 cant connet!")
    exit(1)

session = requests.session()
if http_proxy := os.getenv("HTTP_PROXY"):
    session.proxies.update(http=http_proxy)
if https_proxy := os.getenv("HTTPS_PROXY"):
    session.proxies.update(https=https_proxy)
if proxy := config.get('proxy'):
    session.proxies.update(proxy)

agent = os.getenv("MTA_USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82")
session.headers = {"user-agent": agent}


def add_to_aria2(url: str, save_dir: str):
    logger.info(f"add {url} to aria2")
    if url.startswith("magnet:?"):
        client.add_magnet(url, options={'dir': f'{ARIA2_BASE_DIR}/{save_dir}'})
    else:
        try:
            filename = Path(url).name
        except OSError:
            filename = url[url.rfind("/") + 1:]
        filename_path = torrents_save_dir.joinpath(filename)
        filename_path.parent.mkdir(parents=True, exist_ok=True)
        if not filename_path.exists():
            resp = session.get(url)
            filename_path.write_bytes(resp.content)
        client.add(filename_path.as_posix(), options={'dir': f'{ARIA2_BASE_DIR}/{save_dir}'})


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
                add_to_aria2(download_url, bangumi_name)
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
    with history_path.open(mode='r+', encoding='utf8') as w:
        content = w.read()
        w.seek(0, 0)
        w.write(line + '\n' + content)


@logger.catch
def run():
    logger.info("mikan to aria2 starting")
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
