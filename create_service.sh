#!/bin/bash

DIRECTORY='/tools/Sync_Iptables/'
if [[ ! -d "$DIRECTORY" ]]; then
	sudo mkdir -p $DIRECTORY >>/dev/null 2>&1
fi

sudo cp sync-iptables.service /usr/lib/systemd/system/
sudo ln -s /usr/lib/systemd/system/sync-iptables.service /etc/systemd/system/sync-iptables.service
sudo cp main.py $DIRECTORY

sudo systemctl daemon-reload
sudo systemctl restart sync-iptables.service
sudo systemctl status sync-iptables.service
