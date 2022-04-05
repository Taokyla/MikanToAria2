#!/usr/bin/env bash
. /etc/profile
cd $(dirname $0)
git update
python3 main.py