#!/bin/env bash

sudo docker build . -f /home/scarzehd/Documents/dev/sc_annoy_bot/Dockerfile --tag git.scarzehd.com/scarzehd/sc_annoy_bot
sudo docker push git.scarzehd.com/scarzehd/sc_annoy_bot