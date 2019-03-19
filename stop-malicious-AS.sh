#!/bin/bash

sudo python run.py --node R5 --cmd "pgrep -f [z]ebra-R5 | xargs kill -9"
sudo python run.py --node R5 --cmd "pgrep -f [b]gpd-R5 | xargs kill -9"
