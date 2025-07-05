#!/bin/bash
# 好みで移動（省略しても OK）

set -eu
export HOME=/home/trader
export WINEPREFIX="$HOME/.wine"
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

cd ~/my_project/sh_folder || exit 1

/usr/bin/script -qfc \
  "wine 'C:\\Users\\trader\\AppData\\Local\\Programs\\Python\\Python38\\python.exe' \
        'Z:\\home\\trader\\my_project\\scripts\\spread_logger.py'" \
  /dev/null