#!/bin/bash

# 仮想ディスプレイ上で MT5 をバックグラウンド起動
nohup xvfb-run --auto-servernum --server-args="-screen 0 1024x768x24" \
  wine "C:\\Program Files\\XMTrading MT5\\terminal64.exe" \
  > ~/my_project/mt5.log 2>&1 &

# 少し待ってからログの先頭を表示（オプション）
sleep 5
echo "=== MT5 起動ログ（先頭20行） ==="
head -n 20 ~/my_project/mt5.log
