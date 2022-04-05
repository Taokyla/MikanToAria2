#!/usr/bin/env bash
. /etc/profile
cd $(dirname $0)
git pull
python3 main.py