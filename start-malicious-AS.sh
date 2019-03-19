#!/bin/bash

echo "Killing any existing rogue AS"
./stop-malicious-AS.sh

echo "Starting rogue AS"
sudo python run.py --node R5 --cmd "~/quagga-1.2.4/zebra/zebra -f conf/zebra-R5.conf -d -i /tmp/zebra-R5.pid > logs/R5-zebra-stdout"
sudo python run.py --node R5 --cmd "~/quagga-1.2.4/bgpd/bgpd -f conf/bgpd-R5.conf -d -i /tmp/bgpd-R5.pid > logs/R5-bgpd-stdout"
